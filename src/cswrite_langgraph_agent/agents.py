from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .artifacts import (
    create_task_dir,
    editable_review_block,
    markdown_table,
    new_run_id,
    prepare_demo_repo,
    write_json,
    write_text,
)
from .config import AgentConfig
from .llm import LLMClient
from .mcp_adapter import Retriever
from .state import AgentState


def _append(state: AgentState, message: str) -> None:
    state.setdefault("messages", []).append(message)


def _artifact(state: AgentState, name: str, path: str) -> None:
    state.setdefault("artifacts", {})[name] = path


def _llm_stage_note(state: AgentState, llm: LLMClient | None, stage: str, prompt: str) -> str:
    """在 bailian 模式下真实调用大模型，并把结果沉淀到状态中。

    这里不让模型直接改写结构化字段，避免输出格式随机导致流程不可测；
    模型负责给出阶段判断/风险提示，结构化产物仍由流程代码兜底生成。
    """
    if state.get("llm_mode") != "bailian" or llm is None:
        return ""
    last_error = ""
    for attempt in range(1, 4):
        try:
            text = llm.complete(
                "你是嵌入式烧录器研发 Agent。请输出简洁中文，重点指出判断依据、风险和下一步。",
                prompt,
                temperature=0.1,
            ).strip()
            state.setdefault("llm_calls", []).append(
                {"stage": stage, "status": "ok", "attempt": attempt, "response": text}
            )
            return text
        except Exception as exc:
            last_error = str(exc)
            if attempt < 3:
                time.sleep(2 * attempt)
    message = f"{stage} 阶段大模型调用失败：{last_error}"
    state.setdefault("errors", []).append(message)
    state.setdefault("llm_calls", []).append(
        {"stage": stage, "status": "failed", "attempt": 3, "error": last_error}
    )
    return ""


def _task_dir(state: AgentState) -> Path:
    return Path(state["task_dir"])


def init_run(state: AgentState, cfg: AgentConfig) -> AgentState:
    state = dict(state)
    run_id = state.get("run_id") or new_run_id()
    task_dir, slug = create_task_dir(cfg, state["task"], run_id)
    state["run_id"] = run_id
    state["task_slug"] = slug
    state["task_dir"] = str(task_dir)
    state["stage"] = "init"
    state.setdefault("mode", "demo")
    state.setdefault("llm_mode", "template")
    state.setdefault("auto_approve", False)
    state.setdefault("execute_code", False)
    state.setdefault("save_real_taskpath", False)
    state.setdefault("approved_gates", [])
    state.setdefault("artifacts", {})
    state.setdefault("messages", [])
    state.setdefault("errors", [])
    if state["mode"] == "demo":
        repo_dir = prepare_demo_repo(cfg, task_dir)
    else:
        repo_dir = cfg.code_root
    state["repo_dir"] = str(repo_dir)
    write_json(task_dir / "state_init.json", state)
    _append(state, f"初始化完成：run_id={run_id}")
    return state


def retrieval_agent(state: AgentState, cfg: AgentConfig, retriever: Retriever) -> AgentState:
    state = dict(state)
    state["stage"] = "retrieval"
    retrieval = retriever.retrieve(state["task"], state.get("mode", "demo"), state.get("repo_dir", ""))
    state["retrieval"] = retrieval
    md = [
        f"# 上下文包：{state['task']}",
        "",
        "## 检索来源",
        "",
        "- TaskPath 历史路径",
        "- 文档知识图谱 / 文档检索",
        "- 代码结构 / 示例实现",
        "",
        "## 文档证据",
        "```json",
        json.dumps(retrieval.get("docs", []), ensure_ascii=False, indent=2)[:6000],
        "```",
        "",
        "## 代码证据",
        "```json",
        json.dumps(retrieval.get("code", []), ensure_ascii=False, indent=2)[:6000],
        "```",
        "",
        "## 诊断信息",
        "\n".join(f"- {item}" for item in retrieval.get("diagnostics", [])) or "- 无",
    ]
    path = write_text(_task_dir(state) / "00_context_pack.md", "\n".join(md))
    _artifact(state, "context_pack", path)
    _append(state, "上下文检索完成。")
    return state


def requirement_agent(state: AgentState, cfg: AgentConfig, llm: LLMClient) -> AgentState:
    state = dict(state)
    state["stage"] = "requirement_review"
    items = [
        {
            "req_id": "R1",
            "requirement": "新增 8 位旧 ICP 芯片 VMODEL_TEST_8BIT 的软件侧支持。",
            "source_evidence": "任务输入 + 旧 ICP 芯片参考实现 + 8 位烧录规范",
            "acceptance_criteria": "芯片宏、名称、ops 注册和芯片实现文件均可被代码引用。",
            "user_confirmation": "pending",
            "status": "pending_user_review",
        },
        {
            "req_id": "R2",
            "requirement": "实现时必须复用旧 ICP 通信协议，不误用 SPI 新协议。",
            "source_evidence": "io_icsp 旧 ICP 接口与参考芯片实现",
            "acceptance_criteria": "新芯片实现文件引用 io_icsp.h，芯片操作回调使用旧 ICP 风格。",
            "user_confirmation": "pending",
            "status": "pending_user_review",
        },
        {
            "req_id": "R3",
            "requirement": "测试必须覆盖编码实现、架构设计和需求验收三层。",
            "source_evidence": "当前工作流规则",
            "acceptance_criteria": "05_test_cases.md 与 06_test_execution.md 均按三层分组。",
            "user_confirmation": "pending",
            "status": "pending_user_review",
        },
    ]
    llm_note = _llm_stage_note(
        state,
        llm,
        "requirement_review",
        f"请基于任务和检索证据，总结需求重点和需要人工确认的风险点：\n任务：{state['task']}",
    )
    if llm_note:
        _append(state, f"百炼需求摘要：{llm_note}")
    state["requirement_items"] = items
    body = [
        f"# 需求评审：{state['task']}",
        "",
        markdown_table(
            items,
            [
                "req_id",
                "requirement",
                "source_evidence",
                "acceptance_criteria",
                "user_confirmation",
                "status",
            ],
        ),
        "\n## 大模型阶段判断\n\n" + (llm_note or "- 未启用大模型模式"),
        editable_review_block(),
    ]
    path = write_text(_task_dir(state) / "01_requirement_review.md", "\n".join(body))
    _artifact(state, "requirement_review", path)
    _append(state, "需求评审已生成，等待人工确认。")
    return state


def requirement_gate(state: AgentState) -> AgentState:
    state = dict(state)
    approved = state.get("auto_approve") or "requirement" in state.get("approved_gates", [])
    if approved:
        for item in state.get("requirement_items", []):
            item["user_confirmation"] = "approved"
            item["status"] = "approved"
        state["pending_gate"] = ""
        _append(state, "需求已确认，进入架构设计。")
    else:
        state["pending_gate"] = "requirement"
        _append(state, "流程暂停：请人工审查 01_requirement_review.md。")
    return state


def architecture_agent(state: AgentState, llm: LLMClient | None = None) -> AgentState:
    state = dict(state)
    state["stage"] = "architecture_review"
    layers = [
        {
            "arch_id": "A1",
            "linked_requirement": "R1",
            "layer_module": "芯片编译宏与名称层",
            "design_decision": "在 config_8bit.h 新增 VMODEL_TEST_8BIT 宏和 STR 宏。",
            "interface_dependency": "被 cswrite_cfg_8bit.c 和 UI/配置层引用。",
            "user_confirmation": "pending",
            "status": "pending_user_review",
        },
        {
            "arch_id": "A2",
            "linked_requirement": "R1,R2",
            "layer_module": "芯片操作实现层",
            "design_decision": "新增 VMODEL_TEST_8BIT.c，按 chip_operation 回调模板实现。",
            "interface_dependency": "依赖 io_icsp.h 的旧 ICP 通信接口。",
            "user_confirmation": "pending",
            "status": "pending_user_review",
        },
        {
            "arch_id": "A3",
            "linked_requirement": "R1,R3",
            "layer_module": "注册与调度层",
            "design_decision": "在 cswrite_cfg_8bit.c 注册 extern、OPS 宏、名称列表和 ops 列表。",
            "interface_dependency": "名称列表与 ops 列表索引必须一致。",
            "user_confirmation": "pending",
            "status": "pending_user_review",
        },
    ]
    state["architecture_layers"] = layers
    llm_note = _llm_stage_note(
        state,
        llm,
        "architecture_review",
        "请审查以下架构设计是否能支撑新增旧 ICP 芯片任务，并指出最需要人工确认的点：\n"
        + json.dumps(layers, ensure_ascii=False),
    )
    body = [
        f"# 架构设计评审：{state['task']}",
        "",
        markdown_table(
            layers,
            [
                "arch_id",
                "linked_requirement",
                "layer_module",
                "design_decision",
                "interface_dependency",
                "user_confirmation",
                "status",
            ],
        ),
        "\n## 大模型阶段判断\n\n" + (llm_note or "- 未启用大模型模式"),
        editable_review_block(),
    ]
    path = write_text(_task_dir(state) / "02_architecture_review.md", "\n".join(body))
    _artifact(state, "architecture_review", path)
    _append(state, "架构设计已生成，等待人工确认。")
    return state


def architecture_gate(state: AgentState) -> AgentState:
    state = dict(state)
    approved = state.get("auto_approve") or "architecture" in state.get("approved_gates", [])
    if approved:
        for item in state.get("architecture_layers", []):
            item["user_confirmation"] = "approved"
            item["status"] = "approved"
        state["pending_gate"] = ""
        _append(state, "架构已确认，进入详细设计。")
    else:
        state["pending_gate"] = "architecture"
        _append(state, "流程暂停：请人工审查 02_architecture_review.md。")
    return state


def detailed_design_agent(state: AgentState, llm: LLMClient | None = None) -> AgentState:
    state = dict(state)
    state["stage"] = "detailed_design"
    items = [
        {
            "dd_id": "DD1",
            "linked_arch": "A1",
            "file": "src/common/config_8bit.h",
            "operation": "新增 #define VMODEL_TEST_8BIT，并添加 STR_VMODEL_TEST_8BIT。",
            "symbols": "VMODEL_TEST_8BIT, STR_VMODEL_TEST_8BIT",
            "verification_point": "宏可被 Select-String 检索到。",
        },
        {
            "dd_id": "DD2",
            "linked_arch": "A2",
            "file": "src/middlewave/program/chips/VMODEL_TEST_8BIT.c",
            "operation": "新增芯片实现，包含 io_icsp.h 和 chip_operation 回调结构体。",
            "symbols": "vmodel_test_8bit_ops, chip_operation",
            "verification_point": "文件存在且包含 io_icsp.h、read_id、program、erase。",
        },
        {
            "dd_id": "DD3",
            "linked_arch": "A3",
            "file": "src/common/cswrite_cfg_8bit.c",
            "operation": "注册 extern、OPS 宏、芯片名称列表和 ops 列表。",
            "symbols": "OPS_VMODEL_TEST_8BIT, cswrite_chip_list, cswrite_chip_ops_list",
            "verification_point": "名称列表和 ops 列表都包含新芯片。",
        },
    ]
    state["detailed_design_items"] = items
    llm_note = _llm_stage_note(
        state,
        llm,
        "detailed_design",
        "请检查以下详细设计是否已经具体到文件、函数、宏、变量和验证点，指出遗漏风险：\n"
        + json.dumps(items, ensure_ascii=False),
    )
    body = [
        f"# 详细设计：{state['task']}",
        "",
        markdown_table(items, ["dd_id", "linked_arch", "file", "operation", "symbols", "verification_point"]),
        "\n## 大模型阶段判断\n\n" + (llm_note or "- 未启用大模型模式"),
        editable_review_block(),
    ]
    path = write_text(_task_dir(state) / "03_detailed_design.md", "\n".join(body))
    _artifact(state, "detailed_design", path)
    state["coding_status"] = "plan_only"
    _append(state, "详细设计已生成。")
    return state


def _insert_once(path: Path, marker: str, line: str) -> None:
    text = path.read_text(encoding="utf-8")
    if line in text:
        return
    text = text.replace(marker, line + "\n" + marker)
    path.write_text(text, encoding="utf-8")


def coding_agent(state: AgentState) -> AgentState:
    state = dict(state)
    state["stage"] = "coding"
    repo = Path(state["repo_dir"])
    record: dict[str, Any] = {"modified_files": [], "commands": [], "notes": []}
    if not state.get("execute_code"):
        state["coding_status"] = "plan_only"
        record["notes"].append("当前未开启 execute_code，仅生成编码计划。")
    else:
        cfg_h = repo / "src" / "common" / "config_8bit.h"
        cfg_c = repo / "src" / "common" / "cswrite_cfg_8bit.c"
        chip_c = repo / "src" / "middlewave" / "program" / "chips" / "VMODEL_TEST_8BIT.c"
        _insert_once(cfg_h, "/* CHIP_DEFINE_END */", "#define VMODEL_TEST_8BIT 0x88")
        _insert_once(cfg_h, "/* CHIP_STR_END */", '#define STR_VMODEL_TEST_8BIT "VMODEL_TEST_8BIT"')
        chip_c.write_text(
            "\n".join(
                [
                    '#include "io_icsp.h"',
                    '#include "chip_operation.h"',
                    "",
                    "static int vmodel_test_8bit_read_id(void) { return io_icsp_read_id(); }",
                    "static int vmodel_test_8bit_erase(void) { return io_icsp_chip_erase(); }",
                    "static int vmodel_test_8bit_program(void) { return io_icsp_program(); }",
                    "",
                    "const struct chip_operation vmodel_test_8bit_ops = {",
                    "    .read_id = vmodel_test_8bit_read_id,",
                    "    .erase = vmodel_test_8bit_erase,",
                    "    .program = vmodel_test_8bit_program,",
                    "};",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        _insert_once(
            cfg_c,
            "/* EXTERN_END */",
            "extern const struct chip_operation vmodel_test_8bit_ops;",
        )
        _insert_once(cfg_c, "/* OPS_DEFINE_END */", "#define OPS_VMODEL_TEST_8BIT (&vmodel_test_8bit_ops)")
        _insert_once(cfg_c, "/* CHIP_LIST_END */", "    STR_VMODEL_TEST_8BIT,")
        _insert_once(cfg_c, "/* OPS_LIST_END */", "    OPS_VMODEL_TEST_8BIT,")
        state["coding_status"] = "implemented"
        record["modified_files"] = [str(cfg_h), str(chip_c), str(cfg_c)]
        record["commands"] = [
            "Select-String -Path src/common/config_8bit.h -Pattern VMODEL_TEST_8BIT",
            "Select-String -Path src/common/cswrite_cfg_8bit.c -Pattern OPS_VMODEL_TEST_8BIT",
            "Select-String -Path src/middlewave/program/chips/VMODEL_TEST_8BIT.c -Pattern io_icsp.h",
        ]
    state["coding_record"] = record
    body = [
        f"# 编码记录：{state['task']}",
        "",
        f"- 编码状态：{state['coding_status']}",
        "",
        "## 修改文件",
        "\n".join(f"- {item}" for item in record.get("modified_files", [])) or "- 无",
        "",
        "## 检查命令",
        "\n".join(f"- `{item}`" for item in record.get("commands", [])) or "- 无",
        "",
        "## 备注",
        "\n".join(f"- {item}" for item in record.get("notes", [])) or "- 无",
    ]
    path = write_text(_task_dir(state) / "04_coding_record.md", "\n".join(body))
    _artifact(state, "coding_record", path)
    _append(state, f"编码阶段完成：{state['coding_status']}。")
    return state


def test_design_agent(state: AgentState, cfg: AgentConfig, llm: LLMClient | None = None) -> AgentState:
    state = dict(state)
    state["stage"] = "test_design"
    skill_note = "未读取到 Skill"
    if cfg.skill_path.exists():
        skill_note = f"已读取 Skill：{cfg.skill_path}，长度 {len(cfg.skill_path.read_text(encoding='utf-8'))} 字符"
    cases = {
        "detail_design_verification": [
            {
                "case_id": "TC-DD-001",
                "verify_level": "detail_design_verification",
                "target": "DD1",
                "case_type": "static",
                "steps": "检查 config_8bit.h 是否存在 VMODEL_TEST_8BIT 和 STR 宏。",
                "expected": "两个宏均存在且命名一致。",
            },
            {
                "case_id": "TC-DD-002",
                "verify_level": "detail_design_verification",
                "target": "DD2",
                "case_type": "static",
                "steps": "检查 VMODEL_TEST_8BIT.c 是否包含 io_icsp.h 和 chip_operation。",
                "expected": "使用旧 ICP 接口并导出 vmodel_test_8bit_ops。",
            },
        ],
        "architecture_verification": [
            {
                "case_id": "TC-ARCH-001",
                "verify_level": "architecture_verification",
                "target": "A1+A2+A3",
                "case_type": "integration",
                "steps": "检查编译宏、芯片实现、注册表三层是否形成完整链路。",
                "expected": "名称列表和 ops 列表均包含新芯片，索引关系可维护。",
            }
        ],
        "requirement_acceptance": [
            {
                "case_id": "TC-REQ-001",
                "verify_level": "requirement_acceptance",
                "target": "R1+R2+R3",
                "case_type": "acceptance",
                "steps": "基于需求清单回溯验证旧 ICP 新芯片支持、协议选择和三层测试覆盖。",
                "expected": "所有已确认需求均有设计、代码和测试证据。",
            }
        ],
    }
    state["test_cases"] = {"skill_note": skill_note, "cases": cases}
    llm_note = _llm_stage_note(
        state,
        llm,
        "test_design",
        "请审查以下测试用例是否覆盖编码/详细设计验证、架构验证、需求验收三层，指出缺口：\n"
        + json.dumps(cases, ensure_ascii=False),
    )
    sections = [f"# 测试用例：{state['task']}", "", f"- Skill：{skill_note}", ""]
    for title, rows in [
        ("## 1. 详细设计/编码验证用例", cases["detail_design_verification"]),
        ("## 2. 架构设计验证用例", cases["architecture_verification"]),
        ("## 3. 需求验收用例", cases["requirement_acceptance"]),
    ]:
        sections.extend(
            [
                title,
                "",
                markdown_table(
                    rows,
                    ["case_id", "verify_level", "target", "case_type", "steps", "expected"],
                ),
                "",
            ]
        )
    sections.extend(
        [
            "## 4. 边界值、反例和错误处理用例",
            "",
            "- TC-NEG-001：名称列表存在但 ops 列表缺失时，应判定注册不完整。",
            "- TC-BOUND-001：芯片宏值冲突时，应阻断合入并提示重新分配。",
            "",
            "## 5. 静态检查 / dry-run 命令",
            "",
            "```powershell",
            "Select-String -Path src/common/config_8bit.h -Pattern VMODEL_TEST_8BIT",
            "Select-String -Path src/common/cswrite_cfg_8bit.c -Pattern OPS_VMODEL_TEST_8BIT",
            "Select-String -Path src/middlewave/program/chips/VMODEL_TEST_8BIT.c -Pattern io_icsp.h",
            "```",
            "\n## 大模型阶段判断\n\n" + (llm_note or "- 未启用大模型模式"),
            editable_review_block(),
            "## 执行记录区",
            "",
            "- 待执行",
        ]
    )
    path = write_text(_task_dir(state) / "05_test_cases.md", "\n".join(sections))
    _artifact(state, "test_cases", path)
    _append(state, "测试用例已生成，并保存为可编辑文件。")
    return state


def test_execution_agent(state: AgentState, llm: LLMClient | None = None) -> AgentState:
    state = dict(state)
    state["stage"] = "test_execution"
    repo = Path(state["repo_dir"])

    def exists_text(rel: str, text: str) -> tuple[str, str]:
        path = repo / rel
        if not path.exists():
            return "fail", f"{rel} 不存在"
        content = path.read_text(encoding="utf-8", errors="ignore")
        return ("pass", f"{rel} 包含 {text}") if text in content else ("fail", f"{rel} 未包含 {text}")

    dd_results = []
    for rel, text, target in [
        ("src/common/config_8bit.h", "VMODEL_TEST_8BIT", "DD1"),
        ("src/middlewave/program/chips/VMODEL_TEST_8BIT.c", "io_icsp.h", "DD2"),
        ("src/common/cswrite_cfg_8bit.c", "OPS_VMODEL_TEST_8BIT", "DD3"),
    ]:
        result, evidence = exists_text(rel, text)
        dd_results.append(
            {
                "verify_level": "detail_design_verification",
                "target": target,
                "result": result,
                "evidence": evidence,
                "defect_or_next_action": "" if result == "pass" else "检查编码阶段输出",
            }
        )
    arch_pass = all(item["result"] == "pass" for item in dd_results)
    arch_results = [
        {
            "verify_level": "architecture_verification",
            "target": "A1+A2+A3",
            "result": "pass" if arch_pass else "fail",
            "evidence": "宏定义、芯片实现、注册表三层均存在" if arch_pass else "至少一个详细设计检查失败",
            "defect_or_next_action": "" if arch_pass else "回到详细设计/编码阶段修正",
        }
    ]
    req_results = [
        {
            "verify_level": "requirement_acceptance",
            "target": "R1+R2+R3",
            "result": "pass" if arch_pass else "manual_required",
            "evidence": "demo 静态检查证明软件链路完整；真实烧录需后续接入专用测试环境。",
            "defect_or_next_action": "真实环境接入后补充 real_tool 结果",
        }
    ]
    execution = {
        "execution_mode": "dry_run",
        "test_runner_status": "dry_run_completed",
        "verification_results_by_level": {
            "detail_design_verification": dd_results,
            "architecture_verification": arch_results,
            "requirement_acceptance": req_results,
        },
        "complete_enough_for_demo": arch_pass,
    }
    state["test_execution"] = execution
    llm_note = _llm_stage_note(
        state,
        llm,
        "test_execution",
        "请审查以下测试执行结果是否足以说明三层验证状态，并指出不能等同于真实硬件测试的限制：\n"
        + json.dumps(execution, ensure_ascii=False),
    )
    sections = [f"# 测试执行报告：{state['task']}", "", "- 执行模式：dry_run/static_check", ""]
    for title, rows in [
        ("## 1. 编码/详细设计验证结果", dd_results),
        ("## 2. 架构设计验证结果", arch_results),
        ("## 3. 需求验收验证结果", req_results),
    ]:
        sections.extend(
            [
                title,
                "",
                markdown_table(
                    rows,
                    ["verify_level", "target", "result", "evidence", "defect_or_next_action"],
                ),
                "",
            ]
        )
    sections.extend(
        [
            "## 4. 未完成/人工/硬件依赖项",
            "",
            "- 当前为 dry-run；真实烧录器、目标板、烧录结果日志后续接入后再改为 real_tool。",
            "\n## 大模型阶段判断\n\n" + (llm_note or "- 未启用大模型模式"),
            editable_review_block(),
        ]
    )
    path = write_text(_task_dir(state) / "06_test_execution.md", "\n".join(sections))
    _artifact(state, "test_execution", path)
    _append(state, "测试执行报告已生成，包含三层验证结果。")
    return state


def close_agent(state: AgentState, llm: LLMClient | None = None) -> AgentState:
    state = dict(state)
    state["stage"] = "closed"
    final = {
        "task": state["task"],
        "status": "success" if state.get("test_execution", {}).get("complete_enough_for_demo") else "failed",
        "retrieved_context": state.get("retrieval", {}),
        "approved_requirements": state.get("requirement_items", []),
        "approved_architecture": state.get("architecture_layers", []),
        "detailed_design_items": state.get("detailed_design_items", []),
        "coding_record": state.get("coding_record", {}),
        "test_case_files": [state.get("artifacts", {}).get("test_cases", "")],
        "verification_results_by_level": state.get("test_execution", {}).get("verification_results_by_level", {}),
        "pitfalls": [
            "不要只完成编码验证就保存成功路径。",
            "真实测试环境未接入时必须标记 dry_run/manual/hardware-required。",
        ],
        "next_reuse_hint": "相似新增旧 ICP 芯片任务可优先复用三步注册模式：config_8bit.h -> 新建芯片.c -> cswrite_cfg_8bit.c。",
    }
    state["final_key_path"] = final
    llm_note = _llm_stage_note(
        state,
        llm,
        "closed",
        "请基于最终关键路径，用三句话总结该任务下次如何复用，以及当前验证限制：\n"
        + json.dumps(final, ensure_ascii=False),
    )
    body = [
        f"# 关键成功路径：{state['task']}",
        "",
        "```json",
        json.dumps(final, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 大模型闭环总结",
        "",
        llm_note or "- 未启用大模型模式",
    ]
    path = write_text(_task_dir(state) / "07_key_success_path.md", "\n".join(body))
    _artifact(state, "key_success_path", path)
    _append(state, "闭环摘要已生成，关键成功路径可进入记忆库。")
    return state

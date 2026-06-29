from __future__ import annotations

import json
import re
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
from .context_manager import build_managed_context
from .llm import LLMClient
from .mcp_adapter import Retriever
from .memory import MemoryStore
from .state import AgentState


def _chip_spec(state: AgentState) -> dict[str, Any]:
    """从状态中取出芯片规格。

    规格由 task_analysis_agent 统一生成，后续需求、架构、详细设计、编码、
    测试全部引用它，避免各阶段各自解析任务导致信息漂移。
    """

    return state.get("chip_spec", {})


def _safe_macro_name(text: str) -> str:
    """把任务中的芯片名清洗成 C 宏名。"""

    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", text).strip("_").upper()
    return cleaned or "VMODEL_TEST_8BIT"


def _extract_chip_macro(task: str) -> str:
    """从自然语言任务中提取最像芯片型号的 token。

    面试演示里常见输入类似“新增一个测试用 8 位旧 ICP 芯片 VMODEL_TEST_8BIT”。
    这里优先选择带下划线/数字的英文大写 token；如果没有，就使用稳定 demo 默认值。
    """

    candidates = re.findall(r"\b[A-Z][A-Z0-9_]{2,}\b", task)
    noise = {"ICP", "SPI", "I2C", "UART", "GPIO", "DMA", "ADC"}
    for candidate in candidates:
        if candidate not in noise:
            return _safe_macro_name(candidate)
    return "VMODEL_TEST_8BIT"


def _extract_bit_width(task: str) -> int:
    """识别 8 位/32 位等芯片族；默认走当前示例仓库最完整的 8 位链路。"""

    normalized = task.lower().replace(" ", "")
    if "32位" in normalized or "32bit" in normalized or "32-bit" in normalized:
        return 32
    return 8


def _extract_protocol(task: str) -> str:
    """识别烧录协议，当前 demo 对旧 ICP 链路覆盖最完整。"""

    upper = task.upper()
    if "旧" in task and "ICP" in upper:
        return "old_icp"
    if "ICP" in upper:
        return "icp"
    if "SPI" in upper:
        return "spi"
    return "old_icp"


def _protocol_label(protocol: str) -> str:
    labels = {"old_icp": "旧 ICP", "icp": "ICP", "spi": "SPI"}
    return labels.get(protocol, protocol)


def _next_chip_value(config_path: Path, macro: str) -> str:
    """在现有 config 头文件中分配一个不冲突的十六进制芯片值。

    如果宏已经存在，则复用原值，保证重复执行时幂等。
    """

    if not config_path.exists():
        return "0x88"
    text = config_path.read_text(encoding="utf-8", errors="ignore")
    existing = re.search(rf"^\s*#define\s+{re.escape(macro)}\s+(0x[0-9A-Fa-f]+|\d+)", text, re.M)
    if existing:
        return existing.group(1)
    values: list[int] = []
    for value in re.findall(r"^\s*#define\s+[A-Z0-9_]+\s+(0x[0-9A-Fa-f]+|\d+)", text, re.M):
        try:
            values.append(int(value, 0))
        except ValueError:
            continue
    next_value = max(values, default=0x87) + 1
    return f"0x{next_value:X}"


def _derive_chip_spec(task: str, repo_dir: str) -> dict[str, Any]:
    """把自然语言任务压成后续节点可消费的结构化芯片规格。"""

    macro = _extract_chip_macro(task)
    bit_width = _extract_bit_width(task)
    protocol = _extract_protocol(task)
    symbol_prefix = macro.lower()
    config_file = f"src/common/config_{bit_width}bit.h"
    registry_file = f"src/common/cswrite_cfg_{bit_width}bit.c"
    chip_file = f"src/middlewave/program/chips/{macro}.c"
    repo = Path(repo_dir) if repo_dir else Path()
    value = _next_chip_value(repo / config_file, macro) if repo_dir else "0x88"
    return {
        "chip_macro": macro,
        "chip_string_macro": f"STR_{macro}",
        "chip_value": value,
        "bit_width": bit_width,
        "protocol": protocol,
        "protocol_label": _protocol_label(protocol),
        "symbol_prefix": symbol_prefix,
        "ops_symbol": f"{symbol_prefix}_ops",
        "ops_macro": f"OPS_{macro}",
        "config_file": config_file,
        "registry_file": registry_file,
        "chip_file": chip_file,
        "reference_chip": "CSU32PX10",
        "scope_note": "当前 demo 聚焦旧 ICP 新芯片接入；真实硬件烧录结果通过测试执行阶段标记为后续接入。",
    }


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
    state.setdefault("inject_coding_defect", False)
    state.setdefault("repair_attempts", 0)
    state.setdefault("max_repair_attempts", 1 if state.get("execute_code") else 0)
    state.setdefault("repair_history", [])
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


def task_analysis_agent(state: AgentState, cfg: AgentConfig, llm: LLMClient) -> AgentState:
    """任务理解节点：把用户输入解析成可执行的研发规格。

    这是面试时非常关键的 agent 场景：LLM 可以参与理解，但流程不会完全依赖
    非结构化文本。代码先做确定性解析，再把解析结果交给模型做风险补充。
    """

    state = dict(state)
    state["stage"] = "task_analysis"
    spec = _derive_chip_spec(state["task"], state.get("repo_dir", ""))
    state["chip_spec"] = spec
    llm_note = _llm_stage_note(
        state,
        llm,
        "task_analysis",
        "请检查下面的烧录器研发任务解析是否合理。重点说明芯片型号、位宽、协议、"
        "需要人工确认的风险，不要输出 JSON：\n"
        + json.dumps({"task": state["task"], "chip_spec": spec}, ensure_ascii=False, indent=2),
    )
    analysis = {
        "input_task": state["task"],
        "chip_spec": spec,
        "llm_note": llm_note or "未启用大模型模式，使用确定性解析结果。",
        "agent_scenes": [
            "自然语言任务结构化",
            "LLM 风险审查",
            "确定性规格驱动后续节点",
        ],
    }
    state["task_analysis"] = analysis
    body = [
        f"# 任务解析：{state['task']}",
        "",
        "## 结构化芯片规格",
        "",
        "```json",
        json.dumps(spec, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Agent 场景",
        "",
        "\n".join(f"- {item}" for item in analysis["agent_scenes"]),
        "",
        "## 大模型风险补充",
        "",
        llm_note or "- 未启用大模型模式",
    ]
    path = write_text(_task_dir(state) / "00_task_analysis.md", "\n".join(body))
    _artifact(state, "task_analysis", path)
    _append(state, f"任务解析完成：{spec['chip_macro']} / {spec['protocol_label']}。")
    return state


def planner_agent(state: AgentState, llm: LLMClient | None = None) -> AgentState:
    """Planner 节点：根据任务复杂度决定执行策略。

    这里的 Planner 不只是写说明，它会设置后续控制流使用的修复预算。
    当前 V 模型主链路仍保持稳定；差异化决策主要体现在是否启用自修复、
    最大修复次数、以及哪些节点属于必跑/条件执行。
    """

    state = dict(state)
    state["stage"] = "planner"
    spec = _chip_spec(state)
    task = state.get("task", "")
    complexity_score = 1
    complexity_reasons: list[str] = []
    if state.get("mode") == "real":
        complexity_score += 2
        complexity_reasons.append("real 模式需要接入真实 MCP/代码库")
    if state.get("execute_code"):
        complexity_score += 2
        complexity_reasons.append("开启代码修改，需要测试失败后的修复路径")
    if any(word in task for word in ["完整", "验证", "闭环", "成熟", "自修复"]):
        complexity_score += 1
        complexity_reasons.append("任务要求完整闭环或成熟 Agent 能力")
    if spec.get("protocol") != "old_icp":
        complexity_score += 1
        complexity_reasons.append("协议不是当前 demo 最成熟的旧 ICP 默认链路")

    max_repair_attempts = int(state.get("max_repair_attempts", 1 if state.get("execute_code") else 0))
    plan = {
        "complexity_score": complexity_score,
        "complexity_level": "high" if complexity_score >= 5 else "medium" if complexity_score >= 3 else "low",
        "complexity_reasons": complexity_reasons or ["标准 8 位旧 ICP 新芯片接入"],
        "mandatory_nodes": [
            "task_analysis",
            "retrieval",
            "requirement_review",
            "architecture_review",
            "detailed_design",
            "test_design",
            "test_execution",
            "critic",
            "traceability_matrix",
            "observability",
            "closed",
        ],
        "conditional_nodes": {
            "coding": bool(state.get("execute_code")),
            "reflection": bool(state.get("execute_code") and max_repair_attempts > 0),
            "human_gates": not bool(state.get("auto_approve")),
        },
        "repair_policy": {
            "enabled": bool(state.get("execute_code") and max_repair_attempts > 0),
            "max_repair_attempts": max_repair_attempts,
            "preferred_order": ["coding", "detailed_design"],
            "stop_rule": "达到最大修复次数或 Critic 判定无可自动修复动作后进入闭环失败总结。",
        },
    }
    state["execution_plan"] = plan
    state["repair_attempts"] = int(state.get("repair_attempts", 0))
    state["max_repair_attempts"] = max_repair_attempts
    llm_note = _llm_stage_note(
        state,
        llm,
        "planner",
        "请审查下面的 Agent 执行计划是否合理，重点说明为什么需要或不需要自修复：\n"
        + json.dumps({"task": task, "chip_spec": spec, "plan": plan}, ensure_ascii=False, indent=2),
    )
    body = [
        f"# Planner 执行计划：{state['task']}",
        "",
        "## 计划 JSON",
        "",
        "```json",
        json.dumps(plan, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 大模型阶段判断",
        "",
        llm_note or "- 未启用大模型模式",
    ]
    path = write_text(_task_dir(state) / "00_planner.md", "\n".join(body))
    _artifact(state, "planner", path)
    _append(state, f"Planner 完成：复杂度={plan['complexity_level']}，自修复={plan['repair_policy']['enabled']}。")
    return state


def retrieval_agent(
    state: AgentState,
    cfg: AgentConfig,
    retriever: Retriever,
    memory_store: MemoryStore | None = None,
) -> AgentState:
    state = dict(state)
    state["stage"] = "retrieval"
    spec = _chip_spec(state)
    # 检索 query 同时包含自然语言意图和关键代码符号，能提高 codegraph/MCP 命中率。
    query = " ".join(
        [
            state["task"],
            spec.get("chip_macro", ""),
            spec.get("reference_chip", ""),
            spec.get("config_file", ""),
            spec.get("registry_file", ""),
            "io_icsp",
            "chip_operation",
        ]
    )
    retrieval = retriever.retrieve(query, state.get("mode", "demo"), state.get("repo_dir", ""))
    if memory_store is not None:
        retrieval["memories"] = memory_store.search_memory_items(query, limit=6)
    state["retrieval"] = retrieval
    managed_context = build_managed_context(state["task"], spec, retrieval)
    state["managed_context"] = managed_context
    md = [
        f"# 上下文包：{state['task']}",
        "",
        "## 本次任务规格",
        "```json",
        json.dumps(spec, ensure_ascii=False, indent=2),
        "```",
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
    context_rows = [
        {
            "source_type": item["source_type"],
            "source": item["source"],
            "score": item["score"],
            "char_count": item["char_count"],
        }
        for item in managed_context.get("selected_evidence", [])
    ]
    managed_md = [
        f"# 受控上下文：{state['task']}",
        "",
        "## 上下文预算",
        "",
        "```json",
        json.dumps(managed_context.get("budget", {}), ensure_ascii=False, indent=2),
        "```",
        "",
        "## 关键约束覆盖",
        "",
        "```json",
        json.dumps(managed_context.get("coverage", {}), ensure_ascii=False, indent=2),
        "```",
        "",
        "## 冲突提示",
        "",
        "\n".join(f"- {item}" for item in managed_context.get("conflicts", [])) or "- 无",
        "",
        "## 入选证据索引",
        "",
        markdown_table(context_rows, ["source_type", "source", "score", "char_count"])
        if context_rows
        else "- 无",
        "",
        "## 入选证据摘要",
        "",
    ]
    for index, item in enumerate(managed_context.get("selected_evidence", []), start=1):
        managed_md.extend(
            [
                f"### Evidence {index}: {item['source_type']} / {item['source']}",
                "",
                item["snippet"],
                "",
            ]
        )
    managed_path = write_text(_task_dir(state) / "00_managed_context.md", "\n".join(managed_md))
    _artifact(state, "managed_context", managed_path)
    _append(state, "上下文检索完成。")
    return state


def requirement_agent(state: AgentState, cfg: AgentConfig, llm: LLMClient) -> AgentState:
    state = dict(state)
    state["stage"] = "requirement_review"
    spec = _chip_spec(state)
    items = [
        {
            "req_id": "R1",
            "requirement": (
                f"新增 {spec.get('bit_width', 8)} 位 {spec.get('protocol_label', '旧 ICP')} "
                f"芯片 {spec.get('chip_macro', 'VMODEL_TEST_8BIT')} 的软件侧支持。"
            ),
            "source_evidence": "任务输入 + 旧 ICP 芯片参考实现 + 8 位烧录规范 + 上下文检索结果",
            "acceptance_criteria": (
                f"{spec.get('config_file')} 中存在芯片宏与名称宏，"
                f"{spec.get('chip_file')} 存在实现文件，"
                f"{spec.get('registry_file')} 完成 ops 注册。"
            ),
            "user_confirmation": "pending",
            "status": "pending_user_review",
        },
        {
            "req_id": "R2",
            "requirement": f"实现时必须复用 {spec.get('protocol_label', '旧 ICP')} 通信协议，不误用其他新协议。",
            "source_evidence": "io_icsp 旧 ICP 接口、chip_operation 回调与参考芯片实现",
            "acceptance_criteria": (
                f"{spec.get('chip_file')} 引用 io_icsp.h，"
                "read_id/erase/program 回调均走旧 ICP 风格接口。"
            ),
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
        "请基于任务、结构化规格和检索证据，总结需求重点和需要人工确认的风险点：\n"
        + json.dumps(
            {
                "task": state["task"],
                "chip_spec": spec,
                "retrieval_diagnostics": state.get("retrieval", {}).get("diagnostics", []),
            },
            ensure_ascii=False,
            indent=2,
        ),
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
    spec = _chip_spec(state)
    layers = [
        {
            "arch_id": "A1",
            "linked_requirement": "R1",
            "layer_module": "芯片编译宏与名称层",
            "design_decision": (
                f"在 {spec.get('config_file')} 新增 {spec.get('chip_macro')} "
                f"和 {spec.get('chip_string_macro')}。"
            ),
            "interface_dependency": f"被 {spec.get('registry_file')} 和 UI/配置层引用。",
            "user_confirmation": "pending",
            "status": "pending_user_review",
        },
        {
            "arch_id": "A2",
            "linked_requirement": "R1,R2",
            "layer_module": "芯片操作实现层",
            "design_decision": f"新增 {spec.get('chip_file')}，按 chip_operation 回调模板实现。",
            "interface_dependency": f"依赖 io_icsp.h 的 {spec.get('protocol_label')} 通信接口。",
            "user_confirmation": "pending",
            "status": "pending_user_review",
        },
        {
            "arch_id": "A3",
            "linked_requirement": "R1,R3",
            "layer_module": "注册与调度层",
            "design_decision": (
                f"在 {spec.get('registry_file')} 注册 extern、{spec.get('ops_macro')}、"
                "名称列表和 ops 列表。"
            ),
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
    spec = _chip_spec(state)
    items = [
        {
            "dd_id": "DD1",
            "linked_arch": "A1",
            "file": spec.get("config_file", "src/common/config_8bit.h"),
            "operation": (
                f"新增 #define {spec.get('chip_macro')} {spec.get('chip_value')}，"
                f"并添加 {spec.get('chip_string_macro')}。"
            ),
            "symbols": f"{spec.get('chip_macro')}, {spec.get('chip_string_macro')}",
            "verification_point": "宏可被 Select-String 检索到。",
        },
        {
            "dd_id": "DD2",
            "linked_arch": "A2",
            "file": spec.get("chip_file", "src/middlewave/program/chips/VMODEL_TEST_8BIT.c"),
            "operation": "新增芯片实现，包含 io_icsp.h 和 chip_operation 回调结构体。",
            "symbols": f"{spec.get('ops_symbol')}, chip_operation",
            "verification_point": "文件存在且包含 io_icsp.h、read_id、program、erase。",
        },
        {
            "dd_id": "DD3",
            "linked_arch": "A3",
            "file": spec.get("registry_file", "src/common/cswrite_cfg_8bit.c"),
            "operation": "注册 extern、OPS 宏、芯片名称列表和 ops 列表。",
            "symbols": f"{spec.get('ops_macro')}, cswrite_chip_list, cswrite_chip_ops_list",
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


def _insert_once(path: Path, marker: str, line: str) -> str:
    """在 marker 前插入一行，保证重复执行不会重复写入。"""

    text = path.read_text(encoding="utf-8")
    if line in text:
        return "exists"
    if marker not in text:
        raise ValueError(f"{path} 未找到插入标记 {marker}")
    text = text.replace(marker, line + "\n" + marker)
    path.write_text(text, encoding="utf-8")
    return "inserted"


def coding_agent(state: AgentState) -> AgentState:
    state = dict(state)
    state["stage"] = "coding"
    repo = Path(state["repo_dir"])
    spec = _chip_spec(state)
    record: dict[str, Any] = {
        "chip_spec": spec,
        "modified_files": [],
        "commands": [],
        "notes": [],
        "insertions": [],
    }
    cfg_h = repo / spec.get("config_file", "src/common/config_8bit.h")
    cfg_c = repo / spec.get("registry_file", "src/common/cswrite_cfg_8bit.c")
    chip_c = repo / spec.get("chip_file", "src/middlewave/program/chips/VMODEL_TEST_8BIT.c")
    planned_files = [str(cfg_h), str(chip_c), str(cfg_c)]
    if not state.get("execute_code"):
        state["coding_status"] = "plan_only"
        record["notes"].append("当前未开启 execute_code，仅生成编码计划。")
        record["modified_files"] = planned_files
    else:
        try:
            missing = [str(path) for path in [cfg_h, cfg_c] if not path.exists()]
            if missing:
                raise FileNotFoundError("编码依赖文件不存在：" + "；".join(missing))
            chip_c.parent.mkdir(parents=True, exist_ok=True)
            inject_defect = bool(state.get("inject_coding_defect")) and int(
                state.get("repair_attempts", 0)
            ) == 0
            insertions = [
                _insert_once(
                    cfg_h,
                    "/* CHIP_DEFINE_END */",
                    f"#define {spec['chip_macro']} {spec['chip_value']}",
                ),
                _insert_once(
                    cfg_h,
                    "/* CHIP_STR_END */",
                    f'#define {spec["chip_string_macro"]} "{spec["chip_macro"]}"',
                ),
            ]
            if inject_defect:
                record["notes"].append(
                    "故障注入：首轮编码故意跳过注册表写入，用于演示 Critic/Reflection 自修复。"
                )
            else:
                insertions.extend(
                    [
                        _insert_once(
                            cfg_c,
                            "/* EXTERN_END */",
                            f"extern const struct chip_operation {spec['ops_symbol']};",
                        ),
                        _insert_once(
                            cfg_c,
                            "/* OPS_DEFINE_END */",
                            f"#define {spec['ops_macro']} (&{spec['ops_symbol']})",
                        ),
                        _insert_once(cfg_c, "/* CHIP_LIST_END */", f"    {spec['chip_string_macro']},"),
                        _insert_once(cfg_c, "/* OPS_LIST_END */", f"    {spec['ops_macro']},"),
                    ]
                )
            chip_c.write_text(
                "\n".join(
                    [
                        '#include "io_icsp.h"',
                        '#include "chip_operation.h"',
                        "",
                        f"static int {spec['symbol_prefix']}_read_id(void) {{ return io_icsp_read_id(); }}",
                        f"static int {spec['symbol_prefix']}_erase(void) {{ return io_icsp_chip_erase(); }}",
                        f"static int {spec['symbol_prefix']}_program(void) {{ return io_icsp_program(); }}",
                        "",
                        f"const struct chip_operation {spec['ops_symbol']} = {{",
                        f"    .read_id = {spec['symbol_prefix']}_read_id,",
                        f"    .erase = {spec['symbol_prefix']}_erase,",
                        f"    .program = {spec['symbol_prefix']}_program,",
                        "};",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            state["coding_status"] = "implemented"
            if inject_defect:
                state["coding_status"] = "implemented_with_injected_defect"
            record["modified_files"] = planned_files
            record["insertions"] = insertions
            record["commands"] = [
                f"Select-String -Path {spec['config_file']} -Pattern {spec['chip_macro']}",
                f"Select-String -Path {spec['registry_file']} -Pattern {spec['ops_macro']}",
                f"Select-String -Path {spec['chip_file']} -Pattern io_icsp.h",
            ]
        except Exception as exc:
            state["coding_status"] = "failed"
            message = f"编码阶段失败：{exc}"
            state.setdefault("errors", []).append(message)
            record["notes"].append(message)
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
    spec = _chip_spec(state)
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
                "steps": (
                    f"检查 {spec.get('config_file')} 是否存在 {spec.get('chip_macro')} "
                    f"和 {spec.get('chip_string_macro')}。"
                ),
                "expected": "两个宏均存在且命名一致。",
            },
            {
                "case_id": "TC-DD-002",
                "verify_level": "detail_design_verification",
                "target": "DD2",
                "case_type": "static",
                "steps": f"检查 {spec.get('chip_file')} 是否包含 io_icsp.h 和 chip_operation。",
                "expected": f"使用 {spec.get('protocol_label')} 接口并导出 {spec.get('ops_symbol')}。",
            },
            {
                "case_id": "TC-DD-003",
                "verify_level": "detail_design_verification",
                "target": "DD3",
                "case_type": "static",
                "steps": f"检查 {spec.get('registry_file')} 是否注册 {spec.get('ops_macro')}。",
                "expected": "extern、OPS 宏、芯片名称列表、ops 列表四处同时存在。",
            },
        ],
        "architecture_verification": [
            {
                "case_id": "TC-ARCH-001",
                "verify_level": "architecture_verification",
                "target": "A1+A2+A3",
                "case_type": "integration",
                "steps": "检查编译宏、芯片实现、注册表三层是否形成完整链路。",
                "expected": f"{spec.get('chip_string_macro')} 与 {spec.get('ops_macro')} 均进入注册表。",
            }
        ],
        "requirement_acceptance": [
            {
                "case_id": "TC-REQ-001",
                "verify_level": "requirement_acceptance",
                "target": "R1+R2+R3",
                "case_type": "acceptance",
                "steps": f"基于需求清单回溯验证 {spec.get('protocol_label')} 新芯片支持、协议选择和三层测试覆盖。",
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
            f"Select-String -Path {spec.get('config_file')} -Pattern {spec.get('chip_macro')}",
            f"Select-String -Path {spec.get('registry_file')} -Pattern {spec.get('ops_macro')}",
            f"Select-String -Path {spec.get('chip_file')} -Pattern io_icsp.h",
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
    spec = _chip_spec(state)

    def exists_text(rel: str, text: str) -> tuple[str, str]:
        path = repo / rel
        if not path.exists():
            return "fail", f"{rel} 不存在"
        content = path.read_text(encoding="utf-8", errors="ignore")
        return ("pass", f"{rel} 包含 {text}") if text in content else ("fail", f"{rel} 未包含 {text}")

    # 详细设计验证：每个 DD 条目都落到具体文件和符号。
    dd_checks = [
        (spec.get("config_file", "src/common/config_8bit.h"), spec.get("chip_macro", ""), "DD1"),
        (spec.get("config_file", "src/common/config_8bit.h"), spec.get("chip_string_macro", ""), "DD1"),
        (spec.get("chip_file", ""), "io_icsp.h", "DD2"),
        (spec.get("chip_file", ""), spec.get("ops_symbol", ""), "DD2"),
        (spec.get("registry_file", ""), spec.get("ops_macro", ""), "DD3"),
        (spec.get("registry_file", ""), spec.get("chip_string_macro", ""), "DD3"),
    ]
    dd_results = []
    for rel, text, target in dd_checks:
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
            "evidence": (
                f"{spec.get('chip_macro')} 宏定义、芯片实现、注册表三层均存在"
                if arch_pass
                else "至少一个详细设计检查失败"
            ),
            "defect_or_next_action": "" if arch_pass else "回到详细设计/编码阶段修正",
        }
    ]
    protocol_result, protocol_evidence = exists_text(spec.get("chip_file", ""), "io_icsp")
    req_results = [
        {
            "verify_level": "requirement_acceptance",
            "target": "R1",
            "result": "pass" if arch_pass else "manual_required",
            "evidence": "demo 静态检查证明软件链路完整；真实烧录需后续接入专用测试环境。",
            "defect_or_next_action": "真实环境接入后补充 real_tool 结果",
        },
        {
            "verify_level": "requirement_acceptance",
            "target": "R2",
            "result": protocol_result,
            "evidence": protocol_evidence,
            "defect_or_next_action": "" if protocol_result == "pass" else "检查协议头文件和回调实现",
        },
        {
            "verify_level": "requirement_acceptance",
            "target": "R3",
            "result": "pass" if state.get("test_cases", {}).get("cases") else "fail",
            "evidence": "测试用例按 detail_design_verification / architecture_verification / requirement_acceptance 三层生成。",
            "defect_or_next_action": "",
        },
    ]
    all_req_pass = all(item["result"] == "pass" for item in req_results)
    execution = {
        "execution_mode": "dry_run",
        "test_runner_status": "dry_run_completed",
        "verification_results_by_level": {
            "detail_design_verification": dd_results,
            "architecture_verification": arch_results,
            "requirement_acceptance": req_results,
        },
        "complete_enough_for_demo": arch_pass and all_req_pass,
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


def _test_failures(state: AgentState) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    by_level = state.get("test_execution", {}).get("verification_results_by_level", {})
    for level, rows in by_level.items():
        for row in rows:
            if row.get("result") != "pass":
                failures.append(
                    {
                        "level": level,
                        "target": row.get("target", ""),
                        "result": row.get("result", ""),
                        "evidence": row.get("evidence", ""),
                        "next_action": row.get("defect_or_next_action", ""),
                    }
                )
    return failures


def critic_agent(state: AgentState, llm: LLMClient | None = None) -> AgentState:
    """Critic 节点：检查需求、设计、代码、测试之间的矛盾。

    Critic 不直接修代码，只负责给出结构化问题、严重程度和建议回退节点。
    后续由 Reflection 节点决定是否消耗一次修复预算。
    """

    state = dict(state)
    state["stage"] = "critic"
    spec = _chip_spec(state)
    issues: list[dict[str, Any]] = []

    for item in state.get("requirement_items", []):
        if (
            item.get("req_id") == "R1"
            and spec.get("chip_macro")
            and spec["chip_macro"] not in item.get("requirement", "")
        ):
            issues.append(
                {
                    "issue_id": f"CRIT-REQ-{item.get('req_id')}",
                    "severity": "medium",
                    "category": "requirement_consistency",
                    "evidence": f"需求 {item.get('req_id')} 未明确包含芯片宏 {spec.get('chip_macro')}",
                    "repair_target": "requirement_review",
                }
            )

    expected_files = {
        spec.get("config_file", ""),
        spec.get("chip_file", ""),
        spec.get("registry_file", ""),
    }
    designed_files = {item.get("file", "") for item in state.get("detailed_design_items", [])}
    missing_design = sorted(file for file in expected_files if file and file not in designed_files)
    if missing_design:
        issues.append(
            {
                "issue_id": "CRIT-DD-FILES",
                "severity": "high",
                "category": "design_code_alignment",
                "evidence": "详细设计缺少目标文件：" + "；".join(missing_design),
                "repair_target": "detailed_design",
            }
        )

    for failure in _test_failures(state):
        target = str(failure.get("target", ""))
        repair_target = "coding" if target in {"DD1", "DD2", "DD3", "A1+A2+A3", "R1", "R2"} else "test_design"
        issues.append(
            {
                "issue_id": f"CRIT-TEST-{len(issues) + 1:03d}",
                "severity": "high",
                "category": "test_failure",
                "evidence": failure.get("evidence", ""),
                "repair_target": repair_target,
                "test_level": failure.get("level", ""),
                "test_target": target,
            }
        )

    if state.get("coding_status") in {"failed", "implemented_with_injected_defect"}:
        issues.append(
            {
                "issue_id": "CRIT-CODING-STATUS",
                "severity": "high",
                "category": "coding_status",
                "evidence": f"编码状态为 {state.get('coding_status')}",
                "repair_target": "coding",
            }
        )

    repair_attempts = int(state.get("repair_attempts", 0))
    max_repair_attempts = int(state.get("max_repair_attempts", 0))
    can_repair = bool(
        issues
        and state.get("execute_code")
        and repair_attempts < max_repair_attempts
    )
    priority = ["coding", "detailed_design", "test_design", "requirement_review"]
    targets = [issue.get("repair_target", "") for issue in issues]
    recommended_target = next((target for target in priority if target in targets), "")
    report = {
        "status": "pass" if not issues else "fail",
        "issue_count": len(issues),
        "issues": issues,
        "can_repair": can_repair,
        "recommended_repair_target": recommended_target if can_repair else "",
        "repair_attempts": repair_attempts,
        "max_repair_attempts": max_repair_attempts,
    }
    state["critic_report"] = report
    llm_note = _llm_stage_note(
        state,
        llm,
        "critic",
        "请作为 Critic 审查以下需求、设计、代码和测试一致性报告。"
        "如果存在问题，请判断回退到哪个阶段最合理。"
        "注意：repair_attempts>0 代表此前已经修复过；如果当前 status=pass 且 issue_count=0，"
        "应判定为“修复后通过”，不要误判为状态矛盾：\n"
        + json.dumps(report, ensure_ascii=False, indent=2),
    )
    body = [
        f"# Critic 一致性审查：{state['task']}",
        "",
        "## 结论",
        "",
        f"- 状态：{report['status']}",
        f"- 问题数：{report['issue_count']}",
        f"- 可自动修复：{report['can_repair']}",
        f"- 建议回退节点：{report['recommended_repair_target'] or '无'}",
        "",
        "## 问题明细",
        "",
        markdown_table(
            issues,
            ["issue_id", "severity", "category", "evidence", "repair_target"],
        )
        if issues
        else "- 无",
        "",
        "## 大模型阶段判断",
        "",
        llm_note or "- 未启用大模型模式",
    ]
    path = write_text(_task_dir(state) / "10_critic_report.md", "\n".join(body))
    _artifact(state, "critic_report", path)
    _append(state, f"Critic 审查完成：{report['status']}，问题数={report['issue_count']}。")
    return state


def reflection_agent(state: AgentState, llm: LLMClient | None = None) -> AgentState:
    """Reflection 节点：失败后总结原因并决定回退阶段。"""

    state = dict(state)
    state["stage"] = "reflection"
    critic = state.get("critic_report", {})
    repair_attempts = int(state.get("repair_attempts", 0)) + 1
    target = critic.get("recommended_repair_target") or "traceability_matrix"
    if target not in {"coding", "detailed_design", "test_design"}:
        target = "traceability_matrix"
    reflection = {
        "attempt": repair_attempts,
        "reason": "Critic 发现需求、设计、代码或测试之间存在不一致。",
        "critic_status": critic.get("status", ""),
        "critic_issue_count": critic.get("issue_count", 0),
        "next_node": target,
        "repair_actions": [],
    }
    if target == "coding":
        reflection["repair_actions"] = [
            "重新执行编码节点，补齐缺失的宏、芯片实现或注册表项。",
            "保留详细设计不变，优先修复代码事实与设计之间的缺口。",
        ]
    elif target == "detailed_design":
        reflection["repair_actions"] = [
            "重新生成详细设计，补齐缺失文件、符号或验证点。",
            "随后重新编码和测试。",
        ]
    elif target == "test_design":
        reflection["repair_actions"] = [
            "重新生成测试用例，补齐缺失的验证层级或 target 映射。",
            "随后重新执行测试。",
        ]
    else:
        reflection["repair_actions"] = ["无可自动修复动作，进入失败闭环总结。"]

    state["repair_attempts"] = repair_attempts
    state["reflection_report"] = reflection
    state.setdefault("repair_history", []).append(reflection)
    llm_note = _llm_stage_note(
        state,
        llm,
        "reflection",
        "请基于 Critic 报告和修复计划，总结失败原因和下一步回退动作：\n"
        + json.dumps({"critic": critic, "reflection": reflection}, ensure_ascii=False, indent=2),
    )
    body = [
        f"# Reflection 修复决策：{state['task']}",
        "",
        "## 修复决策",
        "",
        "```json",
        json.dumps(reflection, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 大模型阶段判断",
        "",
        llm_note or "- 未启用大模型模式",
    ]
    path = write_text(_task_dir(state) / f"11_reflection_attempt_{repair_attempts}.md", "\n".join(body))
    _artifact(state, f"reflection_attempt_{repair_attempts}", path)
    _append(state, f"Reflection 决策完成：回退到 {target}，attempt={repair_attempts}。")
    return state


def traceability_matrix_agent(state: AgentState) -> AgentState:
    """生成 V 模型追溯矩阵。

    成熟研发 Agent 不能只输出一堆阶段文档，还要证明需求、架构、详细设计、
    代码修改和测试结果能互相追溯。这个节点就是面试时的强证据。
    """

    state = dict(state)
    state["stage"] = "traceability_matrix"
    requirements = state.get("requirement_items", [])
    architecture = state.get("architecture_layers", [])
    details = state.get("detailed_design_items", [])
    test_cases = state.get("test_cases", {}).get("cases", {})
    execution_by_level = state.get("test_execution", {}).get("verification_results_by_level", {})

    case_targets: dict[str, list[str]] = {}
    for rows in test_cases.values():
        for case in rows:
            case_targets.setdefault(str(case.get("target", "")), []).append(str(case.get("case_id", "")))

    execution_targets: dict[str, list[str]] = {}
    for rows in execution_by_level.values():
        for item in rows:
            execution_targets.setdefault(str(item.get("target", "")), []).append(str(item.get("result", "")))

    rows: list[dict[str, Any]] = []
    for req in requirements:
        req_id = str(req.get("req_id", ""))
        linked_arch = [
            item for item in architecture if req_id in str(item.get("linked_requirement", "")).split(",")
        ]
        arch_ids = [str(item.get("arch_id", "")) for item in linked_arch]
        linked_dd = [
            item for item in details if str(item.get("linked_arch", "")) in arch_ids
        ]
        dd_ids = [str(item.get("dd_id", "")) for item in linked_dd]
        code_files = sorted({str(item.get("file", "")) for item in linked_dd if item.get("file")})
        cases = []
        for target in [req_id, "+".join(arch_ids), "+".join(dd_ids), "R1+R2+R3"]:
            cases.extend(case_targets.get(target, []))
        cases.extend(case_targets.get(req_id, []))
        req_results = execution_targets.get(req_id, [])
        legacy_result = execution_targets.get("R1+R2+R3", [])
        all_results = req_results or legacy_result
        status = "pass" if all_results and all(result == "pass" for result in all_results) else "gap"
        rows.append(
            {
                "requirement_id": req_id,
                "requirement": req.get("requirement", ""),
                "architecture_ids": ", ".join(arch_ids) or "缺失",
                "detail_design_ids": ", ".join(dd_ids) or "缺失",
                "code_files": "<br>".join(code_files) or "缺失",
                "test_cases": ", ".join(sorted(set(cases))) or "缺失",
                "execution_result": ", ".join(all_results) or "缺失",
                "trace_status": status,
            }
        )

    complete = bool(rows) and all(row["trace_status"] == "pass" for row in rows)
    matrix = {
        "complete": complete,
        "rows": rows,
        "gaps": [row for row in rows if row["trace_status"] != "pass"],
    }
    state["traceability_matrix"] = matrix
    body = [
        f"# V 模型追溯矩阵：{state['task']}",
        "",
        "## 追溯结论",
        "",
        f"- 完整性：{'pass' if complete else 'gap'}",
        f"- 需求数量：{len(rows)}",
        f"- 缺口数量：{len(matrix['gaps'])}",
        "",
        "## 需求到测试追溯",
        "",
        markdown_table(
            rows,
            [
                "requirement_id",
                "architecture_ids",
                "detail_design_ids",
                "code_files",
                "test_cases",
                "execution_result",
                "trace_status",
            ],
        )
        if rows
        else "- 无",
        "",
        "## 缺口明细",
        "",
        markdown_table(
            matrix["gaps"],
            [
                "requirement_id",
                "requirement",
                "architecture_ids",
                "detail_design_ids",
                "test_cases",
                "execution_result",
                "trace_status",
            ],
        )
        if matrix["gaps"]
        else "- 无",
    ]
    path = write_text(_task_dir(state) / "08_traceability_matrix.md", "\n".join(body))
    _artifact(state, "traceability_matrix", path)
    _append(state, "V 模型追溯矩阵已生成。")
    return state


def observability_agent(state: AgentState, memory_store: MemoryStore) -> AgentState:
    """生成 Agent 观测报告。

    观测报告回答面试官常问的问题：每个节点跑了多久、模型调用是否成功、
    产物是否齐全、记忆写入策略是什么、MCP 检索有没有降级。
    """

    state = dict(state)
    state["stage"] = "observability"
    observability = state.setdefault("observability", {})
    node_runs = observability.get("node_runs", [])
    llm_calls = state.get("llm_calls", [])
    retrieval = state.get("retrieval", {})
    artifacts = state.get("artifacts", {})
    total_elapsed_ms = round(sum(float(item.get("elapsed_ms", 0)) for item in node_runs), 2)
    llm_ok = sum(1 for item in llm_calls if item.get("status") == "ok")
    llm_failed = sum(1 for item in llm_calls if item.get("status") != "ok")
    report = {
        "run_id": state.get("run_id", ""),
        "task": state.get("task", ""),
        "total_elapsed_ms_before_report": total_elapsed_ms,
        "node_count_before_report": len(node_runs),
        "artifact_count": len(artifacts),
        "llm": {
            "mode": state.get("llm_mode", "template"),
            "calls": len(llm_calls),
            "ok": llm_ok,
            "failed": llm_failed,
        },
        "retrieval": {
            "diagnostics": retrieval.get("diagnostics", []),
            "doc_hit_type": type(retrieval.get("docs")).__name__,
            "code_hit_type": type(retrieval.get("code")).__name__,
            "memory_hits": len(retrieval.get("memories", []) or []),
        },
        "context": {
            "selected_count": state.get("managed_context", {}).get("selected_count", 0),
            "coverage": state.get("managed_context", {}).get("coverage", {}),
            "conflicts": state.get("managed_context", {}).get("conflicts", []),
        },
        "traceability": {
            "complete": state.get("traceability_matrix", {}).get("complete", False),
            "gap_count": len(state.get("traceability_matrix", {}).get("gaps", [])),
        },
        "memory_counts_before_close": memory_store.memory_counts(),
        "errors": state.get("errors", []),
    }
    observability["report"] = report
    node_rows = [
        {
            "node": item.get("node", ""),
            "stage": item.get("stage", ""),
            "elapsed_ms": item.get("elapsed_ms", ""),
            "artifact_count": item.get("artifact_count", ""),
            "llm_call_count": item.get("llm_call_count", ""),
            "error_count": item.get("error_count", ""),
        }
        for item in node_runs
    ]
    llm_rows = [
        {
            "stage": item.get("stage", ""),
            "status": item.get("status", ""),
            "attempt": item.get("attempt", ""),
            "preview": str(item.get("response") or item.get("error") or "")[:120],
        }
        for item in llm_calls
    ]
    body = [
        f"# Agent 观测报告：{state['task']}",
        "",
        "## 总览",
        "",
        "```json",
        json.dumps(report, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 节点运行统计",
        "",
        markdown_table(
            node_rows,
            ["node", "stage", "elapsed_ms", "artifact_count", "llm_call_count", "error_count"],
        )
        if node_rows
        else "- 无",
        "",
        "## LLM 调用统计",
        "",
        markdown_table(llm_rows, ["stage", "status", "attempt", "preview"]) if llm_rows else "- 无",
        "",
        "## 检索与上下文管理",
        "",
        f"- 记忆命中数：{report['retrieval']['memory_hits']}",
        f"- 上下文入选证据数：{report['context']['selected_count']}",
        f"- 关键约束覆盖率：{report['context']['coverage'].get('coverage_ratio', 0)}",
        f"- 上下文冲突数：{len(report['context']['conflicts'])}",
        "",
        "## 记忆库分层计数",
        "",
        "```json",
        json.dumps(report["memory_counts_before_close"], ensure_ascii=False, indent=2),
        "```",
    ]
    path = write_text(_task_dir(state) / "09_observability_report.md", "\n".join(body))
    _artifact(state, "observability_report", path)
    _append(state, "Agent 观测报告已生成。")
    return state


def close_agent(state: AgentState, llm: LLMClient | None = None) -> AgentState:
    state = dict(state)
    state["stage"] = "closed"
    spec = _chip_spec(state)
    final_status = (
        "success"
        if state.get("test_execution", {}).get("complete_enough_for_demo")
        and state.get("traceability_matrix", {}).get("complete")
        and state.get("critic_report", {}).get("status") == "pass"
        else "failed"
    )
    final = {
        "task": state["task"],
        "status": final_status,
        "chip_spec": spec,
        "managed_context_summary": {
            "selected_count": state.get("managed_context", {}).get("selected_count", 0),
            "coverage": state.get("managed_context", {}).get("coverage", {}),
            "conflicts": state.get("managed_context", {}).get("conflicts", []),
        },
        "retrieved_context": state.get("retrieval", {}),
        "approved_requirements": state.get("requirement_items", []),
        "approved_architecture": state.get("architecture_layers", []),
        "detailed_design_items": state.get("detailed_design_items", []),
        "coding_record": state.get("coding_record", {}),
        "test_case_files": [state.get("artifacts", {}).get("test_cases", "")],
        "verification_results_by_level": state.get("test_execution", {}).get("verification_results_by_level", {}),
        "traceability_matrix": state.get("traceability_matrix", {}),
        "critic_report": state.get("critic_report", {}),
        "reflection_history": state.get("repair_history", []),
        "observability_report": state.get("observability", {}).get("report", {}),
        "pitfalls": [
            "不要只完成编码验证就保存成功路径。",
            "名称列表和 ops 列表必须同步维护，否则 UI 展示和操作调度会错位。",
            "真实测试环境未接入时必须标记 dry_run/manual/hardware-required。",
        ],
        "agent_engineering_evidence": {
            "langgraph_nodes": [
                "task_analysis",
                "planner",
                "retrieval",
                "requirement_review",
                "architecture_review",
                "detailed_design",
                "coding",
                "test_design",
                "test_execution",
                "critic",
                "reflection",
                "traceability_matrix",
                "observability",
                "closed",
            ],
            "llm_call_count": len(state.get("llm_calls", [])),
            "human_gates": ["requirement", "architecture"],
            "memory_policy": "仅 closed 且 status=success 时写入 success_paths，避免失败路径污染记忆库。",
        },
        "next_reuse_hint": (
            f"相似新增 {spec.get('protocol_label', '旧 ICP')} 芯片任务可复用三步注册模式："
            f"{spec.get('config_file')} -> {spec.get('chip_file')} -> {spec.get('registry_file')}。"
        ),
    }
    state["final_key_path"] = final
    llm_note = _llm_stage_note(
        state,
        llm,
        "closed",
        "请基于最终关键路径，用三句话总结该任务下次如何复用，以及当前验证限制：\n"
        + json.dumps(final, ensure_ascii=False),
    )
    final["agent_engineering_evidence"]["llm_call_count"] = len(state.get("llm_calls", []))
    state["final_key_path"] = final
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

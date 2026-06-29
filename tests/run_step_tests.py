from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from cswrite_langgraph_agent.config import get_config
from cswrite_langgraph_agent.graph import run_workflow
from cswrite_langgraph_agent.memory import MemoryStore


def assert_file(path: str, contains: str = "") -> None:
    p = Path(path)
    assert p.exists(), f"文件不存在: {p}"
    if contains:
        text = p.read_text(encoding="utf-8")
        assert contains in text, f"{p} 未包含 {contains}"


def main() -> None:
    cfg = get_config()
    if cfg.runs_root.exists():
        shutil.rmtree(cfg.runs_root)
    if cfg.memory_db.exists():
        cfg.memory_db.unlink()

    task = "新增一个测试用 8 位旧 ICP 芯片 VMODEL_TEST_8BIT，验证完整研发流程"

    print("[1] 测试人工 Gate：不自动确认时应停在需求评审")
    s1 = run_workflow(
        {
            "task": task,
            "mode": "demo",
            "llm_mode": "template",
            "auto_approve": False,
            "execute_code": False,
        },
        cfg,
    )
    assert s1["pending_gate"] == "requirement"
    assert_file(s1["artifacts"]["requirement_review"], "人工审查与补充区")
    print("    OK")

    print("[2] 测试端到端自动确认 + 示例代码修改")
    s2 = run_workflow(
        {
            "task": task,
            "mode": "demo",
            "llm_mode": "template",
            "auto_approve": True,
            "execute_code": True,
        },
        cfg,
    )
    assert s2["stage"] == "closed"
    assert s2["coding_status"] == "implemented"
    assert s2["final_key_path"]["status"] == "success"
    for key in [
        "task_analysis",
        "planner",
        "context_pack",
        "managed_context",
        "requirement_review",
        "architecture_review",
        "detailed_design",
        "coding_record",
        "test_cases",
        "test_execution",
        "critic_report",
        "traceability_matrix",
        "observability_report",
        "key_success_path",
    ]:
        assert_file(s2["artifacts"][key])
    assert_file(s2["artifacts"]["test_cases"], "architecture_verification")
    assert_file(s2["artifacts"]["test_execution"], "requirement_acceptance")
    assert_file(s2["artifacts"]["managed_context"], "关键约束覆盖")
    assert_file(s2["artifacts"]["traceability_matrix"], "V 模型追溯矩阵")
    assert_file(s2["artifacts"]["observability_report"], "节点运行统计")
    assert s2["managed_context"]["selected_count"] > 0
    assert s2["critic_report"]["status"] == "pass"
    assert s2["traceability_matrix"]["complete"] is True
    assert s2["observability"]["report"]["artifact_count"] >= 10
    assert_file(
        str(Path(s2["repo_dir"]) / "src/middlewave/program/chips/VMODEL_TEST_8BIT.c"),
        "io_icsp.h",
    )
    print("    OK")

    print("[3] 测试 Critic/Reflection 自修复：首轮漏注册表，回退 coding 后成功")
    s_repair = run_workflow(
        {
            "task": "新增一个测试用 8 位旧 ICP 芯片 VMODEL_REPAIR_8BIT，验证自修复流程",
            "mode": "demo",
            "llm_mode": "template",
            "auto_approve": True,
            "execute_code": True,
            "inject_coding_defect": True,
            "max_repair_attempts": 1,
        },
        cfg,
    )
    assert s_repair["stage"] == "closed"
    assert s_repair["final_key_path"]["status"] == "success"
    assert s_repair["critic_report"]["status"] == "pass"
    assert s_repair["repair_attempts"] == 1
    assert len(s_repair["repair_history"]) == 1
    assert s_repair["repair_history"][0]["next_node"] == "coding"
    assert_file(s_repair["artifacts"]["reflection_attempt_1"], "Reflection 修复决策")
    assert_file(
        str(Path(s_repair["repo_dir"]) / "src/common/cswrite_cfg_8bit.c"),
        "OPS_VMODEL_REPAIR_8BIT",
    )
    print("    OK")

    print("[4] 测试 SQLite 关键成功路径记忆")
    memories = MemoryStore(cfg.memory_db).search_success_paths("旧 ICP 芯片 VMODEL_TEST_8BIT")
    assert memories, "没有写入 success_paths"
    assert "next_reuse_hint" in memories[0]
    layered = MemoryStore(cfg.memory_db).search_memory_items("旧 ICP VMODEL_TEST_8BIT", limit=10)
    memory_types = {item["_memory_type"] for item in layered}
    assert {"episodic", "procedural", "semantic"}.issubset(memory_types), memory_types
    print("    OK")

    print("[5] 测试未执行编码时不会保存成功路径")
    s3 = run_workflow(
        {
            "task": "只做设计不执行编码的旧 ICP 芯片任务",
            "mode": "demo",
            "llm_mode": "template",
            "auto_approve": True,
            "execute_code": False,
        },
        cfg,
    )
    assert s3["final_key_path"]["status"] == "failed"
    failed_memories = [
        item
        for item in MemoryStore(cfg.memory_db).search_success_paths("只做设计不执行编码", limit=10)
        if item.get("task") == "只做设计不执行编码的旧 ICP 芯片任务"
    ]
    assert not failed_memories, "失败任务不应进入 success_paths"
    negative = MemoryStore(cfg.memory_db).search_memory_items(
        "只做设计不执行编码", limit=10, memory_types=["negative"]
    )
    assert negative, "失败任务应写入 negative memory"
    print("    OK")

    print("[6] 测试状态可恢复读取")
    loaded = MemoryStore(cfg.memory_db).load_state(s2["run_id"])
    assert loaded["stage"] == "closed"
    print("    OK")

    print("\n全部测试通过")
    print(f"最新 run_id: {s2['run_id']}")
    print(f"任务目录: {s2['task_dir']}")


if __name__ == "__main__":
    main()

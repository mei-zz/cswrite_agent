from __future__ import annotations

from typing import Any, Literal, TypedDict


Stage = Literal[
    "init",
    "retrieval",
    "requirement_review",
    "architecture_review",
    "detailed_design",
    "coding",
    "test_design",
    "test_execution",
    "closed",
]


class AgentState(TypedDict, total=False):
    """LangGraph 中流转的状态。

    这个状态既是流程上下文，也是可持久化的恢复点。人工 Gate 之后可以从
    SQLite 读取该 JSON，补充 approval 后继续往下跑。
    """

    run_id: str
    task: str
    mode: Literal["demo", "real"]
    llm_mode: Literal["template", "bailian"]
    auto_approve: bool
    execute_code: bool
    save_real_taskpath: bool
    resume_from: str
    stage: Stage
    task_slug: str
    task_dir: str
    repo_dir: str
    approved_gates: list[str]
    pending_gate: str
    messages: list[str]
    llm_calls: list[dict[str, Any]]
    artifacts: dict[str, str]
    retrieval: dict[str, Any]
    requirement_items: list[dict[str, Any]]
    architecture_layers: list[dict[str, Any]]
    detailed_design_items: list[dict[str, Any]]
    coding_status: str
    coding_record: dict[str, Any]
    test_cases: dict[str, Any]
    test_execution: dict[str, Any]
    final_key_path: dict[str, Any]
    errors: list[str]

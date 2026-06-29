from __future__ import annotations

from typing import Any, Literal, TypedDict


Stage = Literal[
    "init",
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
    chip_spec: dict[str, Any]
    task_analysis: dict[str, Any]
    execution_plan: dict[str, Any]
    retrieval: dict[str, Any]
    managed_context: dict[str, Any]
    requirement_items: list[dict[str, Any]]
    architecture_layers: list[dict[str, Any]]
    detailed_design_items: list[dict[str, Any]]
    coding_status: str
    coding_record: dict[str, Any]
    test_cases: dict[str, Any]
    test_execution: dict[str, Any]
    critic_report: dict[str, Any]
    reflection_report: dict[str, Any]
    repair_history: list[dict[str, Any]]
    repair_attempts: int
    max_repair_attempts: int
    inject_coding_defect: bool
    traceability_matrix: dict[str, Any]
    observability: dict[str, Any]
    final_key_path: dict[str, Any]
    errors: list[str]

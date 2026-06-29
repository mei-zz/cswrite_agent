from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

from langgraph.graph import END, START, StateGraph

from .agents import (
    architecture_agent,
    architecture_gate,
    close_agent,
    coding_agent,
    critic_agent,
    detailed_design_agent,
    init_run,
    planner_agent,
    reflection_agent,
    requirement_agent,
    requirement_gate,
    retrieval_agent,
    observability_agent,
    task_analysis_agent,
    test_design_agent,
    test_execution_agent,
    traceability_matrix_agent,
)
from .artifacts import write_json
from .config import AgentConfig, get_config
from .llm import LLMClient
from .mcp_adapter import Retriever
from .memory import MemoryStore
from .state import AgentState


def _persisting(
    fn: Callable[[AgentState], AgentState], store: MemoryStore, node_name: str
) -> Callable[[AgentState], AgentState]:
    """包装节点：每个节点结束后持久化状态和阶段事件。"""

    def wrapped(state: AgentState) -> AgentState:
        started = time.perf_counter()
        new_state = fn(state)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        observability = new_state.setdefault("observability", {})
        observability.setdefault("node_runs", []).append(
            {
                "node": node_name,
                "stage": new_state.get("stage", "unknown"),
                "elapsed_ms": elapsed_ms,
                "artifact_count": len(new_state.get("artifacts", {})),
                "llm_call_count": len(new_state.get("llm_calls", [])),
                "error_count": len(new_state.get("errors", [])),
            }
        )
        if "run_id" in new_state:
            store.save_state(dict(new_state))
            store.add_event(
                new_state["run_id"],
                new_state.get("stage", "unknown"),
                {
                    "stage": new_state.get("stage"),
                    "pending_gate": new_state.get("pending_gate", ""),
                    "coding_status": new_state.get("coding_status", ""),
                    "artifacts": new_state.get("artifacts", {}),
                    "elapsed_ms": elapsed_ms,
                },
            )
            task_dir = new_state.get("task_dir")
            if task_dir:
                write_json(Path(task_dir) / "state_latest.json", dict(new_state))
        return new_state

    return wrapped


def build_graph(cfg: AgentConfig | None = None):
    cfg = cfg or get_config()
    store = MemoryStore(cfg.memory_db)
    retriever = Retriever(cfg)
    llm = LLMClient(cfg)

    graph = StateGraph(AgentState)

    graph.add_node("route_entry", lambda state: state)
    graph.add_node("init_run", _persisting(lambda state: init_run(state, cfg), store, "init_run"))
    graph.add_node(
        "task_analysis",
        _persisting(lambda state: task_analysis_agent(state, cfg, llm), store, "task_analysis"),
    )
    graph.add_node(
        "planner",
        _persisting(lambda state: planner_agent(state, llm), store, "planner"),
    )
    graph.add_node(
        "retrieval",
        _persisting(lambda state: retrieval_agent(state, cfg, retriever, store), store, "retrieval"),
    )
    graph.add_node(
        "requirement_review",
        _persisting(
            lambda state: requirement_agent(state, cfg, llm), store, "requirement_review"
        ),
    )
    graph.add_node("requirement_gate", _persisting(requirement_gate, store, "requirement_gate"))
    graph.add_node(
        "architecture_review",
        _persisting(
            lambda state: architecture_agent(state, llm), store, "architecture_review"
        ),
    )
    graph.add_node("architecture_gate", _persisting(architecture_gate, store, "architecture_gate"))
    graph.add_node(
        "detailed_design",
        _persisting(lambda state: detailed_design_agent(state, llm), store, "detailed_design"),
    )
    graph.add_node("coding", _persisting(coding_agent, store, "coding"))
    graph.add_node(
        "test_design",
        _persisting(lambda state: test_design_agent(state, cfg, llm), store, "test_design"),
    )
    graph.add_node(
        "test_execution",
        _persisting(lambda state: test_execution_agent(state, llm), store, "test_execution"),
    )
    graph.add_node(
        "critic",
        _persisting(lambda state: critic_agent(state, llm), store, "critic"),
    )
    graph.add_node(
        "reflection",
        _persisting(lambda state: reflection_agent(state, llm), store, "reflection"),
    )
    graph.add_node(
        "traceability_matrix",
        _persisting(traceability_matrix_agent, store, "traceability_matrix"),
    )
    graph.add_node(
        "observability",
        _persisting(lambda state: observability_agent(state, store), store, "observability"),
    )
    graph.add_node("closed", _persisting(lambda state: close_agent(state, llm), store, "closed"))

    def route_entry(state: AgentState) -> str:
        resume_from = state.get("resume_from", "")
        if resume_from in {
            "task_analysis",
            "planner",
            "retrieval",
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
        }:
            return resume_from
        return "init_run"

    def route_requirement_gate(state: AgentState) -> str:
        return END if state.get("pending_gate") == "requirement" else "architecture_review"

    def route_architecture_gate(state: AgentState) -> str:
        return END if state.get("pending_gate") == "architecture" else "detailed_design"

    def route_critic(state: AgentState) -> str:
        report = state.get("critic_report", {})
        if report.get("status") == "pass":
            return "traceability_matrix"
        if report.get("can_repair"):
            return "reflection"
        return "traceability_matrix"

    def route_reflection(state: AgentState) -> str:
        next_node = state.get("reflection_report", {}).get("next_node", "traceability_matrix")
        if next_node in {"coding", "detailed_design", "test_design"}:
            return next_node
        return "traceability_matrix"

    graph.add_edge(START, "route_entry")
    graph.add_conditional_edges(
        "route_entry",
        route_entry,
        {
            "init_run": "init_run",
            "task_analysis": "task_analysis",
            "planner": "planner",
            "retrieval": "retrieval",
            "architecture_review": "architecture_review",
            "detailed_design": "detailed_design",
            "coding": "coding",
            "test_design": "test_design",
            "test_execution": "test_execution",
            "critic": "critic",
            "reflection": "reflection",
            "traceability_matrix": "traceability_matrix",
            "observability": "observability",
            "closed": "closed",
        },
    )
    graph.add_edge("init_run", "task_analysis")
    graph.add_edge("task_analysis", "planner")
    graph.add_edge("planner", "retrieval")
    graph.add_edge("retrieval", "requirement_review")
    graph.add_edge("requirement_review", "requirement_gate")
    graph.add_conditional_edges(
        "requirement_gate",
        route_requirement_gate,
        {"architecture_review": "architecture_review", END: END},
    )
    graph.add_edge("architecture_review", "architecture_gate")
    graph.add_conditional_edges(
        "architecture_gate",
        route_architecture_gate,
        {"detailed_design": "detailed_design", END: END},
    )
    graph.add_edge("detailed_design", "coding")
    graph.add_edge("coding", "test_design")
    graph.add_edge("test_design", "test_execution")
    graph.add_edge("test_execution", "critic")
    graph.add_conditional_edges(
        "critic",
        route_critic,
        {"reflection": "reflection", "traceability_matrix": "traceability_matrix"},
    )
    graph.add_conditional_edges(
        "reflection",
        route_reflection,
        {
            "coding": "coding",
            "detailed_design": "detailed_design",
            "test_design": "test_design",
            "traceability_matrix": "traceability_matrix",
        },
    )
    graph.add_edge("traceability_matrix", "observability")
    graph.add_edge("observability", "closed")
    graph.add_edge("closed", END)

    compiled = graph.compile()
    return compiled, store


def run_workflow(initial_state: dict[str, Any], cfg: AgentConfig | None = None) -> AgentState:
    app, store = build_graph(cfg)
    state = app.invoke(initial_state)
    if state.get("stage") == "closed" and state.get("final_key_path"):
        if state["final_key_path"].get("status") == "success":
            store.save_success_path(state["run_id"], state["task"], state["final_key_path"])
        store.save_layered_memories(dict(state))
    return state

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from langgraph.graph import END, START, StateGraph

from .agents import (
    architecture_agent,
    architecture_gate,
    close_agent,
    coding_agent,
    detailed_design_agent,
    init_run,
    requirement_agent,
    requirement_gate,
    retrieval_agent,
    test_design_agent,
    test_execution_agent,
)
from .artifacts import write_json
from .config import AgentConfig, get_config
from .llm import LLMClient
from .mcp_adapter import Retriever
from .memory import MemoryStore
from .state import AgentState


def _persisting(
    fn: Callable[[AgentState], AgentState], store: MemoryStore
) -> Callable[[AgentState], AgentState]:
    """包装节点：每个节点结束后持久化状态和阶段事件。"""

    def wrapped(state: AgentState) -> AgentState:
        new_state = fn(state)
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
    graph.add_node("init_run", _persisting(lambda state: init_run(state, cfg), store))
    graph.add_node(
        "retrieval",
        _persisting(lambda state: retrieval_agent(state, cfg, retriever), store),
    )
    graph.add_node(
        "requirement_review",
        _persisting(lambda state: requirement_agent(state, cfg, llm), store),
    )
    graph.add_node("requirement_gate", _persisting(requirement_gate, store))
    graph.add_node(
        "architecture_review",
        _persisting(lambda state: architecture_agent(state, llm), store),
    )
    graph.add_node("architecture_gate", _persisting(architecture_gate, store))
    graph.add_node(
        "detailed_design",
        _persisting(lambda state: detailed_design_agent(state, llm), store),
    )
    graph.add_node("coding", _persisting(coding_agent, store))
    graph.add_node(
        "test_design",
        _persisting(lambda state: test_design_agent(state, cfg, llm), store),
    )
    graph.add_node(
        "test_execution",
        _persisting(lambda state: test_execution_agent(state, llm), store),
    )
    graph.add_node("closed", _persisting(lambda state: close_agent(state, llm), store))

    def route_entry(state: AgentState) -> str:
        resume_from = state.get("resume_from", "")
        if resume_from in {
            "architecture_review",
            "detailed_design",
            "coding",
            "test_design",
            "test_execution",
            "closed",
        }:
            return resume_from
        return "init_run"

    def route_requirement_gate(state: AgentState) -> str:
        return END if state.get("pending_gate") == "requirement" else "architecture_review"

    def route_architecture_gate(state: AgentState) -> str:
        return END if state.get("pending_gate") == "architecture" else "detailed_design"

    graph.add_edge(START, "route_entry")
    graph.add_conditional_edges("route_entry", route_entry)
    graph.add_edge("init_run", "retrieval")
    graph.add_edge("retrieval", "requirement_review")
    graph.add_edge("requirement_review", "requirement_gate")
    graph.add_conditional_edges("requirement_gate", route_requirement_gate)
    graph.add_edge("architecture_review", "architecture_gate")
    graph.add_conditional_edges("architecture_gate", route_architecture_gate)
    graph.add_edge("detailed_design", "coding")
    graph.add_edge("coding", "test_design")
    graph.add_edge("test_design", "test_execution")
    graph.add_edge("test_execution", "closed")
    graph.add_edge("closed", END)

    compiled = graph.compile()
    return compiled, store


def run_workflow(initial_state: dict[str, Any], cfg: AgentConfig | None = None) -> AgentState:
    app, store = build_graph(cfg)
    state = app.invoke(initial_state)
    if (
        state.get("stage") == "closed"
        and state.get("final_key_path")
        and state["final_key_path"].get("status") == "success"
    ):
        store.save_success_path(state["run_id"], state["task"], state["final_key_path"])
    return state

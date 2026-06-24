from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .config import get_config
from .graph import build_graph, run_workflow
from .llm import LLMClient
from .memory import MemoryStore


for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def print_summary(state: dict[str, Any]) -> None:
    print("\n=== 当前结果 ===")
    print(f"run_id: {state.get('run_id')}")
    print(f"当前阶段: {state.get('stage')}")
    print(f"待确认: {state.get('pending_gate') or '无'}")
    print(f"编码状态: {state.get('coding_status', '')}")
    print(f"任务目录: {state.get('task_dir')}")
    print("产物文件:")
    for name, path in state.get("artifacts", {}).items():
        print(f"  - {name}: {path}")
    if state.get("errors"):
        print("错误/降级:")
        for item in state["errors"]:
            print(f"  - {item}")


def cmd_run(args: argparse.Namespace) -> None:
    state = run_workflow(
        {
            "task": args.task,
            "mode": args.mode,
            "llm_mode": args.llm_mode,
            "auto_approve": args.auto_approve,
            "execute_code": args.execute_code,
            "save_real_taskpath": args.save_real_taskpath,
        }
    )
    print_summary(state)


def cmd_resume(args: argparse.Namespace) -> None:
    cfg = get_config()
    store = MemoryStore(cfg.memory_db)
    state = store.load_state(args.run_id)
    approved = set(state.get("approved_gates", []))
    approved.add(args.gate)
    state["approved_gates"] = sorted(approved)
    state["auto_approve"] = args.auto_approve_rest
    if args.gate == "requirement":
        state["resume_from"] = "architecture_review"
    elif args.gate == "architecture":
        state["resume_from"] = "detailed_design"
    else:
        raise ValueError("gate 只能是 requirement 或 architecture")
    final = run_workflow(state, cfg)
    print_summary(final)


def cmd_inspect(args: argparse.Namespace) -> None:
    cfg = get_config()
    state = MemoryStore(cfg.memory_db).load_state(args.run_id)
    print(json.dumps(state, ensure_ascii=False, indent=2))


def cmd_doctor(_: argparse.Namespace) -> None:
    cfg = get_config()
    print("=== 环境检查 ===")
    print(f"project_root: {cfg.project_root}")
    print(f"memory_db: {cfg.memory_db}")
    print(f"skill_path: {cfg.skill_path} exists={cfg.skill_path.exists()}")
    print(f"code_root: {cfg.code_root} exists={cfg.code_root.exists()}")
    print(f"kg_script: {cfg.kg_script} exists={cfg.kg_script.exists()}")
    print(f"taskpath_script: {cfg.taskpath_script} exists={cfg.taskpath_script.exists()}")
    print(f"codegraph_script: {cfg.codegraph_script} exists={cfg.codegraph_script.exists()}")
    print(f"llm_model: {cfg.llm_model}")
    print(f"llm_api_key_present: {bool(cfg.llm_api_key)}")


def cmd_llm_smoke(_: argparse.Namespace) -> None:
    cfg = get_config()
    text = LLMClient(cfg).complete("你是一个测试助手。", "请只回复：pong", temperature=0)
    print(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CSWrite LangGraph 研发 Agent")
    sub = parser.add_subparsers(required=True)

    run = sub.add_parser("run", help="启动一次流程")
    run.add_argument("--task", required=True)
    run.add_argument("--mode", choices=["demo", "real"], default="demo")
    run.add_argument("--llm-mode", choices=["template", "bailian"], default="template")
    run.add_argument("--auto-approve", action="store_true", help="自动通过人工 Gate，用于端到端测试")
    run.add_argument("--execute-code", action="store_true", help="执行示例/真实代码修改")
    run.add_argument("--save-real-taskpath", action="store_true", help="真实模式下额外写入 TaskPath MCP")
    run.set_defaults(func=cmd_run)

    resume = sub.add_parser("resume", help="人工确认后继续执行")
    resume.add_argument("--run-id", required=True)
    resume.add_argument("--gate", choices=["requirement", "architecture"], required=True)
    resume.add_argument("--auto-approve-rest", action="store_true")
    resume.set_defaults(func=cmd_resume)

    inspect = sub.add_parser("inspect", help="查看某次运行状态")
    inspect.add_argument("--run-id", required=True)
    inspect.set_defaults(func=cmd_inspect)

    doctor = sub.add_parser("doctor", help="检查本地依赖路径")
    doctor.set_defaults(func=cmd_doctor)

    llm = sub.add_parser("llm-smoke", help="百炼模型冒烟测试")
    llm.set_defaults(func=cmd_llm_smoke)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

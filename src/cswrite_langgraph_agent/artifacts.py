from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import AgentConfig


def slugify(text: str, limit: int = 42) -> str:
    """把中文/英文任务名压成适合目录名的 slug。"""
    cleaned = re.sub(r"[^\w\u4e00-\u9fff]+", "_", text, flags=re.UNICODE).strip("_")
    return (cleaned or "task")[:limit]


def new_run_id() -> str:
    # 秒级 run_id 在自动化测试里容易撞名；保留时间可读性，同时加入毫秒。
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]


def create_task_dir(cfg: AgentConfig, task: str, run_id: str) -> tuple[Path, str]:
    slug = slugify(task)
    task_dir = cfg.runs_root / f"{run_id}_{slug}"
    task_dir.mkdir(parents=True, exist_ok=True)
    return task_dir, slug


def prepare_demo_repo(cfg: AgentConfig, task_dir: Path) -> Path:
    """端到端测试时复制一份示例仓库，避免修改真实代码。"""
    src = cfg.project_root / "examples" / "fake_cswrite_repo"
    dst = task_dir / "repo"
    if dst.exists():
        return dst
    shutil.copytree(src, dst)
    return dst


def write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def write_json(path: Path, data: Any) -> str:
    return write_text(path, json.dumps(data, ensure_ascii=False, indent=2))


def editable_review_block() -> str:
    return (
        "\n## 人工审查与补充区\n\n"
        "- 审查结论：\n"
        "- 需要修改的条目：\n"
        "- 新增条目：\n"
        "- 删除条目：\n"
        "- 备注：\n"
    )


def markdown_table(rows: list[dict[str, Any]], headers: list[str]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        values = [str(row.get(header, "")).replace("\n", "<br>") for header in headers]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)

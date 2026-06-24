from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


class MemoryStore:
    """SQLite 记忆库。

    - runs：保存每次流程的最新状态，支持人工确认后恢复。
    - events：保存每个阶段的输入/输出摘要，便于调试。
    - success_paths：保存最终可复用的关键路径，替代“每阶段都记忆”的污染做法。
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    task TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS success_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    task TEXT NOT NULL,
                    path_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save_state(self, state: dict[str, Any]) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO runs(run_id, task, stage, state_json, updated_at)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    task=excluded.task,
                    stage=excluded.stage,
                    state_json=excluded.state_json,
                    updated_at=excluded.updated_at
                """,
                (
                    state["run_id"],
                    state.get("task", ""),
                    state.get("stage", ""),
                    json.dumps(state, ensure_ascii=False),
                    now,
                ),
            )

    def load_state(self, run_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("SELECT state_json FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if not row:
            raise KeyError(f"未找到 run_id={run_id}")
        return json.loads(row["state_json"])

    def add_event(self, run_id: str, stage: str, event: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO events(run_id, stage, event_json, created_at) VALUES(?, ?, ?, ?)",
                (
                    run_id,
                    stage,
                    json.dumps(event, ensure_ascii=False),
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )

    def save_success_path(self, run_id: str, task: str, path: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO success_paths(run_id, task, path_json, created_at) VALUES(?, ?, ?, ?)",
                (
                    run_id,
                    task,
                    json.dumps(path, ensure_ascii=False),
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )

    def search_success_paths(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        tokens = [item for item in query.lower().split() if item]
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT run_id, task, path_json, created_at FROM success_paths ORDER BY id DESC LIMIT 50"
            ).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            haystack = (row["task"] + " " + row["path_json"]).lower()
            score = sum(1 for token in tokens if token in haystack)
            if score or not tokens:
                item = json.loads(row["path_json"])
                item["_memory_run_id"] = row["run_id"]
                item["_memory_score"] = score
                item["_created_at"] = row["created_at"]
                results.append(item)
        return sorted(results, key=lambda x: x["_memory_score"], reverse=True)[:limit]


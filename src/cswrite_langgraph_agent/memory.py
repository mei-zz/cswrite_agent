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
    - memory_items：分层长期记忆，区分 episodic/semantic/procedural/negative。
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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_type TEXT NOT NULL,
                    memory_key TEXT NOT NULL,
                    task TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    source_stage TEXT NOT NULL,
                    content_json TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    tags_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memory_items_type_key
                ON memory_items(memory_type, memory_key)
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

    def save_memory_item(
        self,
        *,
        memory_type: str,
        memory_key: str,
        task: str,
        run_id: str,
        source_stage: str,
        content: dict[str, Any],
        confidence: float,
        tags: list[str],
    ) -> None:
        """保存一条分层记忆。

        memory_type 约定：
        - episodic：一次任务经历
        - semantic：领域事实/规则
        - procedural：可复用流程
        - negative：失败路径和禁用经验
        """

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO memory_items(
                    memory_type, memory_key, task, run_id, source_stage,
                    content_json, confidence, tags_json, created_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory_type,
                    memory_key,
                    task,
                    run_id,
                    source_stage,
                    json.dumps(content, ensure_ascii=False),
                    confidence,
                    json.dumps(tags, ensure_ascii=False),
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )

    def search_memory_items(
        self,
        query: str,
        limit: int = 8,
        memory_types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """按关键词召回分层记忆。

        这里使用可解释的轻量检索，方便 demo 稳定；后续可把 content_json 做向量化。
        """

        tokens = [item for item in query.lower().split() if item]
        params: list[Any] = []
        where = ""
        if memory_types:
            where = "WHERE memory_type IN ({})".format(",".join("?" for _ in memory_types))
            params.extend(memory_types)
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT memory_type, memory_key, task, run_id, source_stage,
                       content_json, confidence, tags_json, created_at
                FROM memory_items
                {where}
                ORDER BY id DESC
                LIMIT 100
                """,
                params,
            ).fetchall()

        results: list[dict[str, Any]] = []
        for row in rows:
            haystack = " ".join(
                [
                    row["memory_type"],
                    row["memory_key"],
                    row["task"],
                    row["content_json"],
                    row["tags_json"],
                ]
            ).lower()
            score = sum(1 for token in tokens if token in haystack)
            if score or not tokens:
                item = json.loads(row["content_json"])
                item["_memory_type"] = row["memory_type"]
                item["_memory_key"] = row["memory_key"]
                item["_memory_run_id"] = row["run_id"]
                item["_memory_task"] = row["task"]
                item["_memory_source_stage"] = row["source_stage"]
                item["_memory_confidence"] = row["confidence"]
                item["_memory_tags"] = json.loads(row["tags_json"])
                item["_memory_score"] = score + row["confidence"]
                item["_created_at"] = row["created_at"]
                results.append(item)
        return sorted(results, key=lambda x: x["_memory_score"], reverse=True)[:limit]

    def save_layered_memories(self, state: dict[str, Any]) -> None:
        """根据最终状态写入分层记忆。

        成功任务写入 episodic/procedural/semantic；失败任务只写 negative。
        这样可以避免把未验证方案污染为可复用成功经验。
        """

        run_id = state["run_id"]
        task = state.get("task", "")
        final = state.get("final_key_path", {})
        spec = state.get("chip_spec", {})
        tags = [
            str(spec.get("chip_macro", "")),
            str(spec.get("protocol_label", "")),
            f"{spec.get('bit_width', '')}bit",
            "vmodel",
            "cswrite",
        ]
        if final.get("status") == "success":
            self.save_memory_item(
                memory_type="episodic",
                memory_key=f"run:{run_id}",
                task=task,
                run_id=run_id,
                source_stage="closed",
                content={
                    "summary": "一次完整 V 模型研发闭环成功执行。",
                    "chip_spec": spec,
                    "artifacts": state.get("artifacts", {}),
                    "verification": state.get("test_execution", {}),
                },
                confidence=0.85,
                tags=tags,
            )
            self.save_memory_item(
                memory_type="procedural",
                memory_key=f"procedure:{spec.get('protocol', 'unknown')}:{spec.get('bit_width', 'unknown')}",
                task=task,
                run_id=run_id,
                source_stage="closed",
                content={
                    "procedure": final.get("next_reuse_hint", ""),
                    "traceability_matrix": state.get("traceability_matrix", {}),
                    "pitfalls": final.get("pitfalls", []),
                },
                confidence=0.9,
                tags=tags + ["success_path"],
            )
            self.save_memory_item(
                memory_type="semantic",
                memory_key=f"rule:{spec.get('protocol', 'unknown')}:registration",
                task=task,
                run_id=run_id,
                source_stage="closed",
                content={
                    "fact": "旧 ICP 新芯片接入需要同时维护宏定义、芯片实现、名称列表和 ops 列表。",
                    "evidence": state.get("traceability_matrix", {}).get("rows", []),
                },
                confidence=0.8,
                tags=tags + ["domain_rule"],
            )
        else:
            self.save_memory_item(
                memory_type="negative",
                memory_key=f"failed:{run_id}",
                task=task,
                run_id=run_id,
                source_stage=state.get("stage", "unknown"),
                content={
                    "reason": "流程未通过最终三层验证，不能作为成功路径复用。",
                    "coding_status": state.get("coding_status", ""),
                    "errors": state.get("errors", []),
                    "test_execution": state.get("test_execution", {}),
                },
                confidence=0.75,
                tags=tags + ["failed"],
            )

    def memory_counts(self) -> dict[str, int]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT memory_type, COUNT(*) AS count FROM memory_items GROUP BY memory_type"
            ).fetchall()
        return {row["memory_type"]: int(row["count"]) for row in rows}

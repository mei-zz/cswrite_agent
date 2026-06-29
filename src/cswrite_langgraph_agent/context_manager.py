from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ContextBudget:
    """上下文预算。

    真实大模型上下文窗口虽然越来越大，但成熟 Agent 仍要主动控量：
    只把和当前阶段最相关的证据交给模型，完整原始结果保存在 artifact 中审计。
    """

    max_items_per_source: int = 6
    max_chars_per_item: int = 900
    max_total_chars: int = 9000


def _as_text(value: Any, limit: int) -> str:
    """把任意检索结果稳定转成短文本，供评分和写入上下文包。"""

    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, default=str)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _score_text(text: str, keywords: list[str]) -> float:
    """简单可解释的关键词评分，避免 demo 引入复杂向量依赖。"""

    lowered = text.lower()
    score = 0.0
    for keyword in keywords:
        if keyword and keyword.lower() in lowered:
            score += 1.0
    return score


def _normalize_collection(
    source_type: str,
    values: Any,
    keywords: list[str],
    budget: ContextBudget,
) -> list[dict[str, Any]]:
    """把 docs/code/memory/taskpath 等不同形状的结果统一成 evidence。"""

    if not values:
        return []
    if isinstance(values, dict):
        # 常见 MCP 返回会把列表放到 results/symbols/items 等字段里。
        for key in ("results", "symbols", "items", "data", "matches"):
            if isinstance(values.get(key), list):
                values = values[key]
                break
        else:
            values = [values]
    elif not isinstance(values, list):
        values = [values]

    evidence: list[dict[str, Any]] = []
    for index, item in enumerate(values):
        if isinstance(item, dict):
            source = (
                item.get("source")
                or item.get("file")
                or item.get("path")
                or item.get("document_title")
                or item.get("name")
                or f"{source_type}_{index}"
            )
            raw_score = item.get("score", 0)
        else:
            source = f"{source_type}_{index}"
            raw_score = 0
        text = _as_text(item, budget.max_chars_per_item)
        score = _score_text(text, keywords)
        try:
            score += float(raw_score)
        except (TypeError, ValueError):
            pass
        evidence.append(
            {
                "source_type": source_type,
                "source": str(source),
                "score": round(score, 3),
                "char_count": len(text),
                "snippet": text,
            }
        )
    evidence.sort(key=lambda row: row["score"], reverse=True)
    return evidence[: budget.max_items_per_source]


def _coverage(evidence: list[dict[str, Any]], keywords: list[str]) -> dict[str, Any]:
    """统计关键约束是否被上下文覆盖。"""

    joined = " ".join(item["snippet"].lower() for item in evidence)
    hits = [keyword for keyword in keywords if keyword and keyword.lower() in joined]
    misses = [keyword for keyword in keywords if keyword and keyword.lower() not in joined]
    return {
        "required_keywords": keywords,
        "hit_keywords": hits,
        "missed_keywords": misses,
        "coverage_ratio": round(len(hits) / max(len(keywords), 1), 3),
    }


def _detect_conflicts(task: str, chip_spec: dict[str, Any]) -> list[str]:
    """做少量确定性冲突检测，后续可升级成 Critic 节点。"""

    conflicts: list[str] = []
    if chip_spec.get("bit_width") == 8 and ("32位" in task or "32bit" in task.lower()):
        conflicts.append("任务文本出现 32 位线索，但结构化规格为 8 位。")
    if chip_spec.get("protocol") == "old_icp" and "SPI" in task.upper():
        conflicts.append("任务文本同时出现旧 ICP 和 SPI，请人工确认协议。")
    return conflicts


def build_managed_context(
    task: str,
    chip_spec: dict[str, Any],
    retrieval: dict[str, Any],
    budget: ContextBudget | None = None,
) -> dict[str, Any]:
    """构建后续节点可消费的受控上下文。

    返回内容保留“证据索引”和“被选中的短片段”，既方便模型消费，也方便面试时
    展示上下文工程不是简单拼接文本。
    """

    budget = budget or ContextBudget()
    keywords = [
        chip_spec.get("chip_macro", ""),
        chip_spec.get("chip_string_macro", ""),
        chip_spec.get("ops_macro", ""),
        chip_spec.get("config_file", ""),
        chip_spec.get("registry_file", ""),
        "io_icsp",
        "chip_operation",
        "旧 ICP",
    ]
    evidence: list[dict[str, Any]] = []
    for source_type in ("memories", "taskpaths", "docs", "code"):
        evidence.extend(
            _normalize_collection(source_type, retrieval.get(source_type), keywords, budget)
        )
    evidence.sort(key=lambda row: row["score"], reverse=True)

    selected: list[dict[str, Any]] = []
    total_chars = 0
    for item in evidence:
        if total_chars + item["char_count"] > budget.max_total_chars:
            continue
        selected.append(item)
        total_chars += item["char_count"]

    return {
        "budget": {
            "max_items_per_source": budget.max_items_per_source,
            "max_chars_per_item": budget.max_chars_per_item,
            "max_total_chars": budget.max_total_chars,
            "selected_total_chars": total_chars,
        },
        "keywords": keywords,
        "coverage": _coverage(selected, keywords),
        "conflicts": _detect_conflicts(task, chip_spec),
        "selected_evidence": selected,
        "evidence_count": len(evidence),
        "selected_count": len(selected),
    }

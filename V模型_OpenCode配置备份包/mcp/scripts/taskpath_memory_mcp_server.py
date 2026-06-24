from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP


for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_TASKPATH_DIR = Path(
    os.getenv("TASKPATH_DIR", "C:/Users/meigang90240/Desktop/KG/task_paths")
)
INDEX_FILE = DEFAULT_TASKPATH_DIR / "index.jsonl"
VALID_STATUSES = {"success", "analysis_only", "failed", "draft"}
VALID_TASK_TYPES = {
    "add_chip_config",
    "verify_existing_impl",
    "modify_program_timing",
    "add_protocol_command",
    "modify_file_descriptor",
    "modify_config_macro",
    "add_or_modify_test",
    "bug_fix",
    "workflow_integration",
    "other",
}
VALID_V_MODEL_STAGES = {
    "",
    "requirement_review",
    "architecture_review",
    "detailed_design",
    "coding",
    "test_design",
    "test_execution",
    "closed",
}
VALID_GATE_STATUSES = {
    "",
    "not_required",
    "pending_user_review",
    "approved",
    "rejected",
    "revised",
}
VALID_EXECUTION_MODES = {
    "",
    "not_started",
    "dry_run",
    "static_check",
    "real_tool",
    "manual_only",
}
VALID_CODING_STATUSES = {
    "",
    "not_started",
    "plan_only",
    "implemented",
    "skipped_by_user",
    "failed",
}
VALID_TEST_RUNNER_STATUSES = {
    "",
    "not_configured",
    "dry_run_completed",
    "executed",
    "failed",
    "blocked",
}

mcp = FastMCP(
    "taskpath-memory",
    instructions=(
        "Use these tools to search, validate, and save CSWrite TaskPath records. "
        "Search historical TaskPaths before planning a task. Save a success record "
        "only after verification evidence exists."
    ),
)


def ensure_taskpath_dir() -> None:
    DEFAULT_TASKPATH_DIR.mkdir(parents=True, exist_ok=True)


def compact_text(value: Any, max_chars: int = 1200) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def parse_json_value(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return default
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return default


def parse_record(record_json: str | dict[str, Any]) -> dict[str, Any]:
    record = parse_json_value(record_json, {})
    if not isinstance(record, dict):
        raise ValueError("record_json must be a JSON object.")
    return record


def normalize_status(status: Any) -> str:
    value = str(status or "draft").strip().lower()
    if value not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {value}. Use one of {sorted(VALID_STATUSES)}.")
    return value


def infer_status(record: dict[str, Any]) -> str:
    raw_status = compact_text(record.get("status"))
    status = normalize_status(raw_status or "draft")
    task_type = compact_text(record.get("task_type")).lower()
    if status == "draft" and task_type == "analysis_only":
        return "analysis_only"
    return status


def infer_task_type(record: dict[str, Any], status: str) -> str:
    raw_task_type = compact_text(record.get("task_type")).strip().lower()
    combined_text = " ".join(
        compact_text(record.get(field), 400)
        for field in ("user_task", "title", "short_name", "verification_result")
    )
    lowered_combined = combined_text.lower()

    readonly_markers = ("只做分析", "纯分析", "只读", "不修改", "无代码修改", "analysis only")
    verify_markers = ("验证", "检查", "确认", "是否", "已实现", "是否已经实现", "verify")
    add_markers = ("新增", "添加", "新建", "add")
    if status == "analysis_only" and any(marker in combined_text for marker in readonly_markers):
        if any(marker in combined_text for marker in verify_markers):
            return "verify_existing_impl"

    if raw_task_type == "analysis_only":
        return "verify_existing_impl"
    if raw_task_type in VALID_TASK_TYPES:
        return raw_task_type

    chip_markers = ("芯片", "chip")
    if any(marker in combined_text for marker in add_markers) and any(
        marker in lowered_combined for marker in chip_markers
    ):
        return "add_chip_config"
    if any(marker in combined_text for marker in verify_markers):
        return "verify_existing_impl"
    if raw_task_type:
        return "other"
    return ""


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        parsed = parse_json_value(text, None)
        if isinstance(parsed, list):
            return parsed
        if parsed is not None and not isinstance(parsed, str):
            return [parsed]
        if "\n" in text:
            items = [
                re.sub(r"^\s*[-*]\s*", "", item).strip()
                for item in text.splitlines()
                if item.strip()
            ]
            if items:
                return items
        return [text]
    parsed = parse_json_value(value, value)
    if isinstance(parsed, list):
        return parsed
    return [parsed]


def list_has_content(value: Any) -> bool:
    return any(compact_text(item, 200) for item in as_list(value))


def first_value(item: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = compact_text(item.get(key))
        if value:
            return value
    return ""


def no_modified_files_row() -> list[dict[str, str]]:
    return [{"file": "None", "change": "Analysis only; no files modified."}]


def normalize_modified_files(value: Any, status: str) -> Any:
    rows = as_list(value)
    if not list_has_content(value):
        return no_modified_files_row()
    if status == "analysis_only":
        text = compact_text(value).lower()
        no_change_markers = (
            "none",
            "no files modified",
            "analysis only",
            "仅分析",
            "纯分析",
            "未修改",
            "无修改",
            "无代码修改",
            "不修改",
        )
        if any(marker in text for marker in no_change_markers):
            return no_modified_files_row()
    return rows


def validate_evidence_table(
    value: Any,
    table_name: str,
    left_aliases: tuple[str, ...],
    right_aliases: tuple[str, ...],
) -> list[str]:
    problems: list[str] = []
    rows = as_list(value)
    if not rows:
        return [table_name]
    for index, item in enumerate(rows, 1):
        if not isinstance(item, dict):
            problems.append(f"{table_name}[{index}] must be an object with evidence fields")
            continue
        if not first_value(item, left_aliases):
            problems.append(f"{table_name}[{index}].source")
        if not first_value(item, right_aliases):
            problems.append(f"{table_name}[{index}].why_or_role")
    return problems


def validate_record_object(record: dict[str, Any]) -> dict[str, Any]:
    status = infer_status(record)
    task_type = infer_task_type(record, status)
    workflow_type = compact_text(record.get("workflow_type")).lower()
    v_model_stage = compact_text(record.get("v_model_stage")).lower()
    gate_status = compact_text(record.get("gate_status")).lower()
    execution_mode = compact_text(record.get("execution_mode")).lower()
    coding_status = compact_text(record.get("coding_status")).lower()
    test_runner_status = compact_text(record.get("test_runner_status")).lower()
    missing: list[str] = []
    warnings: list[str] = []

    if not task_type:
        missing.append("task_type")
    elif compact_text(record.get("task_type")).lower() != task_type:
        warnings.append(f"task_type normalized to {task_type}.")
    if task_type and task_type not in VALID_TASK_TYPES:
        warnings.append(f"unknown task_type: {task_type}.")
    if not compact_text(record.get("user_task")):
        missing.append("user_task")
    if v_model_stage and v_model_stage not in VALID_V_MODEL_STAGES:
        warnings.append(f"unknown v_model_stage: {v_model_stage}.")
    if gate_status and gate_status not in VALID_GATE_STATUSES:
        warnings.append(f"unknown gate_status: {gate_status}.")
    if execution_mode and execution_mode not in VALID_EXECUTION_MODES:
        warnings.append(f"unknown execution_mode: {execution_mode}.")
    if coding_status and coding_status not in VALID_CODING_STATUSES:
        warnings.append(f"unknown coding_status: {coding_status}.")
    if test_runner_status and test_runner_status not in VALID_TEST_RUNNER_STATUSES:
        warnings.append(f"unknown test_runner_status: {test_runner_status}.")
    if v_model_stage in {"requirement_review", "architecture_review"} and gate_status == "":
        warnings.append(f"{v_model_stage} should include gate_status.")
    if workflow_type == "cswrite_v_model" or v_model_stage:
        missing.extend(validate_v_model_record(record, status))

    if status == "success":
        required_text = ["edit_pattern", "verification_result", "next_reuse_hint"]
        required_lists = ["used_docs", "used_code_files", "modified_files", "commands_run", "artifact_files"]
        for field in required_text:
            if not compact_text(record.get(field)):
                missing.append(field)
        for field in required_lists:
            if not list_has_content(record.get(field)):
                missing.append(field)
        missing.extend(
            validate_evidence_table(
                record.get("used_docs"),
                "used_docs",
                ("source", "document", "doc", "name", "title"),
                ("why", "why_used", "reason", "usage", "purpose", "role"),
            )
        )
        missing.extend(
            validate_evidence_table(
                record.get("used_code_files"),
                "used_code_files",
                ("file", "symbol", "file_symbol", "path", "source", "name"),
                ("role", "why", "why_used", "reason", "usage", "purpose"),
            )
        )
    elif status == "analysis_only":
        doc_problems = validate_evidence_table(
            record.get("used_docs"),
            "used_docs",
            ("source", "document", "doc", "name", "title"),
            ("why", "why_used", "reason", "usage", "purpose", "role"),
        )
        code_problems = validate_evidence_table(
            record.get("used_code_files"),
            "used_code_files",
            ("file", "symbol", "file_symbol", "path", "source", "name"),
            ("role", "why", "why_used", "reason", "usage", "purpose"),
        )
        missing.extend(doc_problems)
        missing.extend(code_problems)
    elif status == "failed":
        if not compact_text(record.get("pitfalls")):
            warnings.append("failed record should explain pitfalls.")

    return {
        "ok": not missing,
        "status": status,
        "task_type": task_type,
        "missing": list(dict.fromkeys(missing)),
        "warnings": warnings,
    }


def require_text_field(record: dict[str, Any], field: str) -> list[str]:
    return [] if compact_text(record.get(field)) else [field]


def require_list_field(record: dict[str, Any], field: str) -> list[str]:
    return [] if list_has_content(record.get(field)) else [field]


def validate_v_model_record(record: dict[str, Any], status: str) -> list[str]:
    stage = compact_text(record.get("v_model_stage")).lower()
    execution_mode = compact_text(record.get("execution_mode")).lower()
    coding_status = compact_text(record.get("coding_status")).lower()
    missing: list[str] = []

    if not stage:
        missing.append("v_model_stage")
        return missing
    missing.extend(require_text_field(record, "gate_status"))
    missing.extend(require_text_field(record, "execution_mode"))
    missing.extend(require_text_field(record, "coding_status"))
    missing.extend(require_text_field(record, "test_runner_status"))

    if stage == "requirement_review":
        missing.extend(require_text_field(record, "requirement_review"))
        missing.extend(require_text_field(record, "requirement_baseline"))
        missing.extend(require_list_field(record, "requirement_items"))
    elif stage == "architecture_review":
        missing.extend(require_text_field(record, "requirement_baseline"))
        missing.extend(require_text_field(record, "architecture_design"))
        missing.extend(require_text_field(record, "architecture_baseline"))
        missing.extend(require_list_field(record, "architecture_layers"))
    elif stage == "detailed_design":
        missing.extend(require_text_field(record, "requirement_baseline"))
        missing.extend(require_text_field(record, "architecture_baseline"))
        missing.extend(require_text_field(record, "detailed_design"))
        missing.extend(require_list_field(record, "detailed_design_items"))
        missing.extend(require_list_field(record, "traceability_matrix"))
    elif stage == "coding":
        missing.extend(require_text_field(record, "requirement_baseline"))
        missing.extend(require_text_field(record, "architecture_baseline"))
        missing.extend(require_text_field(record, "detailed_design"))
        missing.extend(require_list_field(record, "detailed_design_items"))
        missing.extend(require_text_field(record, "coding_status"))
        if coding_status == "implemented":
            missing.extend(require_list_field(record, "modified_files"))
            missing.extend(require_list_field(record, "traceability_matrix"))
    elif stage == "test_design":
        missing.extend(require_text_field(record, "requirement_baseline"))
        missing.extend(require_text_field(record, "architecture_baseline"))
        missing.extend(require_text_field(record, "detailed_design"))
        missing.extend(require_list_field(record, "detailed_design_items"))
        missing.extend(require_text_field(record, "test_cases"))
        missing.extend(require_list_field(record, "test_case_files"))
        missing.extend(require_list_field(record, "v_model_verification_plan"))
        missing.extend(require_list_field(record, "traceability_matrix"))
    elif stage == "test_execution":
        missing.extend(require_text_field(record, "requirement_baseline"))
        missing.extend(require_text_field(record, "architecture_baseline"))
        missing.extend(require_text_field(record, "detailed_design"))
        missing.extend(require_list_field(record, "detailed_design_items"))
        missing.extend(require_text_field(record, "test_cases"))
        missing.extend(require_list_field(record, "test_case_files"))
        missing.extend(require_text_field(record, "test_execution_report"))
        missing.extend(require_list_field(record, "v_model_verification_plan"))
        missing.extend(require_list_field(record, "verification_results_by_level"))
        missing.extend(require_list_field(record, "traceability_matrix"))
        missing.extend(require_text_field(record, "execution_mode"))
        missing.extend(require_text_field(record, "coding_status"))
        missing.extend(require_text_field(record, "test_runner_status"))
        if coding_status != "implemented" and execution_mode != "dry_run":
            missing.append("execution_mode=dry_run required when coding_status is not implemented")
        if status == "success" and execution_mode != "real_tool":
            missing.append("success test_execution requires execution_mode=real_tool")
    elif stage == "closed":
        missing.extend(require_text_field(record, "requirement_baseline"))
        missing.extend(require_text_field(record, "architecture_baseline"))
        missing.extend(require_text_field(record, "detailed_design"))
        missing.extend(require_list_field(record, "detailed_design_items"))
        missing.extend(require_text_field(record, "test_cases"))
        missing.extend(require_list_field(record, "test_case_files"))
        missing.extend(require_text_field(record, "test_execution_report"))
        missing.extend(require_list_field(record, "v_model_verification_plan"))
        missing.extend(require_list_field(record, "verification_results_by_level"))
        missing.extend(require_list_field(record, "traceability_matrix"))
        if status != "success":
            missing.append("closed stage requires status=success")
        if compact_text(record.get("coding_status")).lower() != "implemented":
            missing.append("closed stage requires coding_status=implemented")
    return missing


def safe_slug(value: str, fallback: str = "taskpath") -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return (slug or fallback)[:80]


def extract_heading(text: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_bullet(text: str, key: str) -> str:
    pattern = rf"^[ \t]*-[ \t]*{re.escape(key)}[ \t]*:[ \t]*(.*)$"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_inline_heading(text: str, key: str) -> str:
    pattern = rf"^##\s+{re.escape(key)}\s+(.+)$"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_section(text: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if not match:
        return ""
    return compact_text(match.group("body"), 1200)


def split_words(text: str) -> set[str]:
    lowered = text.lower()
    tokens = re.findall(r"[A-Za-z0-9_#./+-]+", lowered)
    for chunk in re.findall(r"[\u4e00-\u9fff]+", lowered):
        if len(chunk) <= 4:
            tokens.append(chunk)
            continue
        for size in (2, 3):
            tokens.extend(chunk[index : index + size] for index in range(0, len(chunk) - size + 1))
    return {token for token in tokens if token}


def markdown_table(items: Any, columns: tuple[str, str], keys: tuple[str, str]) -> str:
    rows = as_list(items)
    header = f"| {columns[0]} | {columns[1]} |\n| --- | --- |"
    lines = [header]
    for item in rows:
        if isinstance(item, dict):
            left = first_value(
                item,
                (
                    keys[0],
                    "source",
                    "document",
                    "doc",
                    "file",
                    "symbol",
                    "file_symbol",
                    "path",
                    "name",
                    "title",
                ),
            )
            right = first_value(
                item,
                (
                    keys[1],
                    "role",
                    "why",
                    "why_used",
                    "reason",
                    "usage",
                    "purpose",
                ),
            )
        else:
            left = compact_text(item)
            right = ""
        lines.append(f"| {left} | {right} |")
    if len(lines) == 1:
        lines.append("|  |  |")
    return "\n".join(lines)


def markdown_table_multi(items: Any, columns: tuple[str, ...], keys: tuple[str, ...]) -> str:
    rows = as_list(items)
    header = "| " + " | ".join(columns) + " |\n| " + " | ".join("---" for _ in columns) + " |"
    lines = [header]
    for item in rows:
        if isinstance(item, dict):
            cells = [compact_text(item.get(key), 500) for key in keys]
        else:
            cells = [compact_text(item, 500)] + ["" for _ in columns[1:]]
        lines.append("| " + " | ".join(cells) + " |")
    if len(lines) == 1:
        lines.append("| " + " | ".join("" for _ in columns) + " |")
    return "\n".join(lines)


def markdown_list(items: Any) -> str:
    rows = as_list(items)
    if not rows:
        return "-"
    return "\n".join(f"- {compact_text(item)}" for item in rows)


def render_taskpath(record: dict[str, Any]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = compact_text(record.get("title") or record.get("short_name") or record.get("user_task"), 120)
    task_card = parse_json_value(record.get("task_card"), {})
    if not isinstance(task_card, dict):
        task_card = {}

    status = normalize_status(record.get("status", "draft"))
    task_type = infer_task_type(record, status)
    created_at = compact_text(record.get("created_at") or now)
    project = compact_text(record.get("project") or "CSWrite3.0")
    modified_files = normalize_modified_files(record.get("modified_files"), status)
    v_model_stage = compact_text(record.get("v_model_stage"))
    gate_status = compact_text(record.get("gate_status"))
    execution_mode = compact_text(record.get("execution_mode"))
    coding_status = compact_text(record.get("coding_status"))
    test_runner_status = compact_text(record.get("test_runner_status"))

    tags = compact_text(record.get("tags")) or "[]"

    return f"""# TaskPath: {title}

## Metadata

- task_type: {task_type}
- created_at: {created_at}
- project: {project}
- status: {status}
- v_model_stage: {v_model_stage}
- gate_status: {gate_status}
- execution_mode: {execution_mode}
- coding_status: {coding_status}
- test_runner_status: {test_runner_status}
- tags: {tags}

## User Task

{compact_text(record.get("user_task"), 2000)}

## Task Card

- target_module: {compact_text(task_card.get("target_module") or record.get("target_module"))}
- expected_files: {compact_text(task_card.get("expected_files") or record.get("expected_files"))}
- required_docs: {compact_text(task_card.get("required_docs") or record.get("required_docs"))}
- verification_method: {compact_text(task_card.get("verification_method") or record.get("verification_method"))}
- risk_level: {compact_text(task_card.get("risk_level") or record.get("risk_level"))}

## Artifact Files

{markdown_list(record.get("artifact_files"))}

## Retrieval Summary

{compact_text(record.get("retrieval_summary"), 5000)}

## Code Inspection Summary

{compact_text(record.get("code_inspection_summary"), 5000)}

## V-Model State

- workflow_type: {compact_text(record.get("workflow_type") or "cswrite_v_model")}
- current_stage: {v_model_stage}
- v_direction: {compact_text(record.get("v_direction"), 1000)}
- gate_status: {gate_status}
- execution_mode: {execution_mode}
- coding_status: {coding_status}
- test_runner_status: {test_runner_status}
- gate_decision: {compact_text(record.get("gate_decision"), 2000)}
- next_stage: {compact_text(record.get("next_stage"), 1000)}

## Requirement Review

{compact_text(record.get("requirement_review"), 5000)}

## Requirement Items

{markdown_table_multi(
    record.get("requirement_items"),
    ("Req ID", "Requirement", "Source/Evidence", "Acceptance Criteria", "User Confirmation", "Status"),
    ("req_id", "requirement", "source_evidence", "acceptance_criteria", "user_confirmation", "status"),
)}

## Requirement Confirmation

{compact_text(record.get("requirement_confirmation"), 3000)}

## Requirement Baseline

{compact_text(record.get("requirement_baseline"), 5000)}

## Architecture Design

{compact_text(record.get("architecture_design"), 5000)}

## Architecture Layers

{markdown_table_multi(
    record.get("architecture_layers"),
    ("Arch ID", "Linked Requirement", "Layer/Module", "Design Decision", "Interface/Dependency", "User Confirmation", "Status"),
    ("arch_id", "linked_requirement", "layer_module", "design_decision", "interface_dependency", "user_confirmation", "status"),
)}

## Architecture Confirmation

{compact_text(record.get("architecture_confirmation"), 3000)}

## Architecture Baseline

{compact_text(record.get("architecture_baseline"), 5000)}

## Detailed Design

{compact_text(record.get("detailed_design"), 5000)}

## Detailed Design Items

{markdown_table_multi(
    record.get("detailed_design_items"),
    ("DD ID", "Linked Architecture", "File", "Function/Variable", "Operation", "Verification Point"),
    ("dd_id", "linked_architecture", "file", "function_variable", "operation", "verification_point"),
)}

## Test Cases

{compact_text(record.get("test_cases"), 5000)}

## Test Case Files

{markdown_list(record.get("test_case_files"))}

## V-Model Verification Plan

{markdown_table_multi(
    record.get("v_model_verification_plan"),
    ("Verify Level", "Target", "Linked Detail/Architecture/Requirement", "Test Case", "Case Type", "Expected Result"),
    ("verify_level", "target", "linked_item", "test_case", "case_type", "expected_result"),
)}

## Test Execution Report

{compact_text(record.get("test_execution_report"), 5000)}

## Verification Results By Level

{markdown_table_multi(
    record.get("verification_results_by_level"),
    ("Verify Level", "Target", "Test Case", "Result", "Evidence", "Defect/Next Action"),
    ("verify_level", "target", "test_case", "result", "evidence", "defect_or_next_action"),
)}

## Traceability Matrix

{markdown_table_multi(
    record.get("traceability_matrix"),
    ("Requirement", "Architecture", "Detailed Design", "Code", "Test Case", "Verification Level", "Result"),
    ("requirement", "architecture", "detailed_design", "code", "test_case", "verification_level", "result"),
)}

## Reused TaskPath

{markdown_list(record.get("reused_taskpath"))}

## Used Documents

{markdown_table(record.get("used_docs"), ("Source", "Why Used"), ("source", "why"))}

## Used Code

{markdown_table(record.get("used_code_files"), ("File/Symbol", "Role"), ("file", "role"))}

## Similar Pattern

{compact_text(record.get("similar_pattern"), 3000)}

## Modified Files

{markdown_table(modified_files, ("File", "Change"), ("file", "change"))}

## Edit Pattern

{compact_text(record.get("edit_pattern"), 4000)}

## Commands Run

```powershell
{compact_text(record.get("commands_run"), 4000)}
```

## Verification Result

{compact_text(record.get("verification_result"), 4000)}

## Pitfalls

{compact_text(record.get("pitfalls"), 3000)}

## Next Reuse Hint

{compact_text(record.get("next_reuse_hint"), 2000)}
"""


def record_from_markdown(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    title = extract_heading(text) or path.stem
    status = (
        extract_bullet(text, "status")
        or extract_inline_heading(text, "Status")
        or ("analysis_only" if "analysis_only" in text else "")
    )
    task_type = extract_bullet(text, "task_type") or extract_inline_heading(text, "task_type")
    created_at = extract_bullet(text, "created_at")
    v_model_stage = extract_bullet(text, "v_model_stage") or extract_bullet(text, "current_stage")
    gate_status = extract_bullet(text, "gate_status")
    execution_mode = extract_bullet(text, "execution_mode")
    coding_status = extract_bullet(text, "coding_status")
    test_runner_status = extract_bullet(text, "test_runner_status")
    tags = extract_bullet(text, "tags")
    target_module = extract_bullet(text, "target_module")
    user_task = extract_inline_heading(text, "user_task") or extract_section(text, "User Task")
    record = {
        "id": path.stem,
        "title": title,
        "status": status or "unknown",
        "task_type": task_type,
        "created_at": created_at,
        "v_model_stage": v_model_stage,
        "gate_status": gate_status,
        "execution_mode": execution_mode,
        "coding_status": coding_status,
        "test_runner_status": test_runner_status,
        "tags": tags,
        "target_module": target_module,
        "user_task": user_task,
        "file_path": str(path),
        "text": compact_text(text, 12000),
        "updated_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
    }
    if record["status"] in VALID_STATUSES:
        record["task_type"] = infer_task_type(record, str(record["status"]))
    return record


def read_index() -> list[dict[str, Any]]:
    ensure_taskpath_dir()
    if not INDEX_FILE.exists():
        return rebuild_index()
    rows: list[dict[str, Any]] = []
    for line in INDEX_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def write_index(rows: list[dict[str, Any]]) -> None:
    ensure_taskpath_dir()
    content = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
    if content:
        content += "\n"
    INDEX_FILE.write_text(content, encoding="utf-8")


def rebuild_index() -> list[dict[str, Any]]:
    ensure_taskpath_dir()
    rows: list[dict[str, Any]] = []
    for path in sorted(DEFAULT_TASKPATH_DIR.glob("*.md")):
        if path.name.startswith("_") or path.name.lower() == "readme.md":
            continue
        rows.append(record_from_markdown(path))
    write_index(rows)
    return rows


def upsert_index_record(record: dict[str, Any]) -> None:
    rows = read_index()
    rows = [row for row in rows if row.get("id") != record.get("id")]
    rows.append(record)
    rows.sort(key=lambda row: row.get("updated_at", ""), reverse=True)
    write_index(rows)


@mcp.tool()
def taskpath_status() -> dict[str, Any]:
    """Return TaskPath memory health, folder location, and record counts."""
    rows = read_index()
    by_status: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status") or "unknown")
        by_status[status] = by_status.get(status, 0) + 1
    return {
        "taskpath_dir": str(DEFAULT_TASKPATH_DIR),
        "index_file": str(INDEX_FILE),
        "record_count": len(rows),
        "by_status": by_status,
    }


@mcp.tool()
def taskpath_rebuild_index() -> dict[str, Any]:
    """Rebuild the TaskPath JSONL index from markdown files."""
    rows = rebuild_index()
    return {
        "taskpath_dir": str(DEFAULT_TASKPATH_DIR),
        "index_file": str(INDEX_FILE),
        "record_count": len(rows),
    }


@mcp.tool()
def taskpath_list_recent(limit: int = 10, status: str = "") -> dict[str, Any]:
    """List recent TaskPath records from the local memory index."""
    rows = read_index()
    if status:
        allowed = {item.strip() for item in status.split(",") if item.strip()}
        rows = [row for row in rows if row.get("status") in allowed]
    limit = max(1, min(int(limit), 50))
    return {"results": rows[:limit]}


@mcp.tool()
def taskpath_get(taskpath_id: str) -> dict[str, Any]:
    """Read a TaskPath markdown record by id or filename stem."""
    ensure_taskpath_dir()
    raw = taskpath_id.strip()
    candidates = [
        DEFAULT_TASKPATH_DIR / raw,
        DEFAULT_TASKPATH_DIR / f"{raw}.md",
    ]
    for path in candidates:
        if path.exists() and path.is_file():
            return {
                "id": path.stem,
                "file_path": str(path),
                "record": record_from_markdown(path),
                "content": path.read_text(encoding="utf-8", errors="replace"),
            }
    raise FileNotFoundError(f"TaskPath not found: {taskpath_id}")


@mcp.tool()
def taskpath_search(
    query: str,
    top_k: int = 5,
    task_type: str = "",
    target_module: str = "",
    status: str = "success,analysis_only",
) -> dict[str, Any]:
    """Search historical TaskPaths by task words, code names, document terms, and status."""
    rows = read_index()
    allowed_status = {item.strip() for item in status.split(",") if item.strip()}
    if allowed_status:
        rows = [row for row in rows if str(row.get("status")) in allowed_status]
    if task_type:
        rows = [row for row in rows if task_type.lower() in str(row.get("task_type", "")).lower()]
    if target_module:
        rows = [
            row
            for row in rows
            if target_module.lower()
            in " ".join([str(row.get("target_module", "")), str(row.get("text", ""))]).lower()
        ]

    query_words = split_words(query)
    scored: list[dict[str, Any]] = []
    for row in rows:
        haystack = " ".join(
            [
                str(row.get("title", "")),
                str(row.get("task_type", "")),
                str(row.get("user_task", "")),
                str(row.get("tags", "")),
                str(row.get("target_module", "")),
                str(row.get("text", "")),
            ]
        )
        row_words = split_words(haystack)
        overlap = query_words & row_words
        substring_hits = sum(1 for word in query_words if word and word in haystack.lower())
        score = len(overlap) * 3 + substring_hits
        if score <= 0 and query.strip():
            continue
        item = dict(row)
        item["score"] = score
        item["matched_terms"] = sorted(overlap)[:30]
        item["snippet"] = compact_text(row.get("text"), 1200)
        scored.append(item)

    scored.sort(key=lambda item: (item.get("score", 0), item.get("updated_at", "")), reverse=True)
    top_k = max(1, min(int(top_k), 30))
    return {
        "query": query,
        "filters": {
            "task_type": task_type,
            "target_module": target_module,
            "status": status,
        },
        "results": scored[:top_k],
    }


@mcp.tool()
def taskpath_validate(record_json: str) -> dict[str, Any]:
    """Validate a TaskPath JSON object before saving."""
    record = parse_record(record_json)
    return validate_record_object(record)


@mcp.tool()
def taskpath_save(record_json: str, allow_incomplete: bool = False) -> dict[str, Any]:
    """Save a TaskPath record as markdown and update the JSONL search index.

    record_json must be a JSON object. For status=success, the record must include:
    task_type, user_task, used_docs, used_code_files, modified_files, edit_pattern,
    commands_run, verification_result, and next_reuse_hint.
    """
    ensure_taskpath_dir()
    record = parse_record(record_json)
    validation = validate_record_object(record)
    if not validation["ok"] and not allow_incomplete:
        raise ValueError(
            "TaskPath validation failed. Missing fields: "
            + ", ".join(validation["missing"])
        )

    status = validation["status"]
    record["status"] = status
    record["task_type"] = validation["task_type"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug_source = (
        record.get("short_name")
        or record.get("title")
        or record.get("task_type")
        or "taskpath"
    )
    filename = f"{timestamp}_{safe_slug(str(record.get('task_type') or 'task'))}_{safe_slug(str(slug_source))}.md"
    path = DEFAULT_TASKPATH_DIR / filename
    markdown = render_taskpath(record)
    path.write_text(markdown, encoding="utf-8")

    index_record = record_from_markdown(path)
    index_record["status"] = status
    index_record["task_type"] = compact_text(record.get("task_type"))
    index_record["v_model_stage"] = compact_text(record.get("v_model_stage"))
    index_record["gate_status"] = compact_text(record.get("gate_status"))
    index_record["execution_mode"] = compact_text(record.get("execution_mode"))
    index_record["coding_status"] = compact_text(record.get("coding_status"))
    index_record["test_runner_status"] = compact_text(record.get("test_runner_status"))
    index_record["tags"] = compact_text(record.get("tags"))
    index_record["target_module"] = compact_text(record.get("target_module"))
    index_record["user_task"] = compact_text(record.get("user_task"), 1000)
    upsert_index_record(index_record)

    return {
        "saved": True,
        "id": path.stem,
        "file_path": str(path),
        "status": status,
        "validation": validation,
    }


def self_test() -> None:
    print(json.dumps(taskpath_rebuild_index(), ensure_ascii=False, indent=2))
    print(json.dumps(taskpath_status(), ensure_ascii=False, indent=2))
    print(
        json.dumps(
            taskpath_search("新增 ICP 芯片 config_8bit cswrite_cfg_8bit io_icsp", top_k=3),
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

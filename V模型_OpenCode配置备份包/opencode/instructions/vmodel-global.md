# Global V-Model Software Workflow

This file is the reusable global workflow. It must stay project-agnostic.

Project-specific knowledge, MCP names, code roots, document roots, domain terms, test Skills, and coding conventions must be defined in a project profile, for example:

```text
C:/Users/meigang90240/.config/opencode/instructions/projects/cswrite-project.md
```

## Core Principle

The workflow is a staged software R&D loop with human gates and editable artifacts.

Every stage must produce a Markdown artifact in the current OpenCode workspace. The user must be able to edit that file before the next stage.

Do not keep the only copy in chat.

## Active Project Profile

Before starting a task:

1. Identify the active project profile from the current workspace and the loaded project instructions.
2. If a project profile exists, follow it for domain knowledge, MCP tools, code roots, Skill usage, and checks.
3. If no project profile is available, use this global workflow and ask the user for the missing project profile only when the task cannot proceed.

## Artifact Root

Create all stage artifacts under the currently opened OpenCode workspace:

```text
./vmodel_runs/YYYYMMDD_HHMMSS_<task_slug>/
```

Never write stage artifacts to a fixed external folder unless that folder is the current workspace.

Every normal reply must include the relative artifact path, for example:

```text
产物文件：vmodel_runs/<task>/01_requirement_review.md
```

If a stage artifact cannot be written inside the current workspace, stop and report the write failure.

## Required Stage Files

```text
00_context_pack.md
01_requirement_review.md
02_architecture_review.md
03_detailed_design.md
04_coding_record.md
05_test_cases.md
06_test_execution.md
07_key_success_path.md
```

## Editable Review Block

Every review, design, and test artifact must include:

```text
## 人工审查与补充区

- 审查结论：
- 需要修改的条目：
- 新增条目：
- 删除条目：
- 备注：
```

When the user edits a stage artifact and asks to continue, read the edited artifact before moving to the next stage.

## User-Facing Status

Use concise user-facing labels:

```text
当前阶段：
确认状态：
编码状态：
测试状态：
产物文件：
下一步：
```

Do not expose internal fields such as `v_direction`, `downward`, or `upward` in normal chat.

## Stage 0: Context Pack

Goal: collect only the context needed for the current stage.

Actions:

1. Search reusable memory first when a memory tool exists in the project profile.
2. Search project document knowledge when a document MCP exists.
3. Search project code knowledge when a code MCP exists.
4. Read local files only after retrieval narrows the scope.
5. Save `00_context_pack.md`.

The context pack should include:

- user request
- selected project profile
- retrieved memories
- document evidence
- code evidence
- assumptions
- unresolved questions

## Stage 1: Requirement Review

Goal: understand the user request and turn it into confirmable requirement items.

Actions:

1. Use the context pack.
2. Decompose the request into atomic requirement items.
3. For each item, provide source evidence, assumptions, acceptance criteria, and confirmation status.
4. Save `01_requirement_review.md`.
5. Stop and wait for user confirmation or edits.

Do not produce architecture, detailed design, code changes, or test cases at this stage.

Required fields:

```text
req_id
requirement
source_evidence
assumption_or_risk
acceptance_criteria
user_confirmation
status
```

## Stage 2: Architecture Review

Trigger: requirement items are approved or revised by the user.

Actions:

1. Read the current `01_requirement_review.md`.
2. Map approved requirements to architecture layers, modules, interfaces, dependencies, and design decisions.
3. Save `02_architecture_review.md`.
4. Stop and wait for user confirmation or edits.

Do not write code or generate test cases at this stage.

Required fields:

```text
arch_id
linked_requirement
layer_or_module
design_decision
interface_dependency
impact_scope
user_confirmation
status
```

## Stage 3: Detailed Design

Trigger: architecture decisions are approved or revised by the user.

Actions:

1. Read the current `02_architecture_review.md`.
2. Produce detailed design items down to concrete files, functions, variables, macros, structs, config items, operations, and verification points.
3. Save `03_detailed_design.md`.
4. If the user asked for design only, stop with `coding_status=plan_only`.

Required fields:

```text
dd_id
linked_arch
target_file
target_symbol
operation
implementation_detail
verification_point
risk
```

## Stage 4: Coding

Trigger: detailed design exists and the user asks to implement.

Actions:

1. Read the current `03_detailed_design.md`.
2. Modify only approved files and scopes.
3. Keep changes minimal and consistent with the existing codebase.
4. Run available software checks defined by the project profile.
5. Save `04_coding_record.md`.

Use `coding_status=implemented` only when code was actually changed and checked.

Coding record must include:

- approved detailed design items
- modified files
- changed symbols
- checks or commands run
- result evidence
- remaining risks

## Stage 5: Test Case Design

Trigger: coding is implemented, or the user asks to generate tests from detailed design.

Actions:

1. Read `01_requirement_review.md`, `02_architecture_review.md`, `03_detailed_design.md`, and `04_coding_record.md` when available.
2. Use the test Skill or test generation rules defined by the project profile.
3. Generate test cases in this order:
   - `detail_design_verification`: code and detailed design implementation
   - `architecture_verification`: approved architecture decisions
   - `requirement_acceptance`: approved requirements and acceptance criteria
4. Save complete editable test cases to `05_test_cases.md`.

Required test fields:

```text
case_id
verify_level
target
case_type
precondition
steps
expected_result
linked_requirement
linked_design
linked_code
execution_mode
status
```

## Stage 6: Test Execution

Goal: run available software checks and record evidence. Hardware execution is not required unless the project profile explicitly requires it.

Actions:

1. Read `05_test_cases.md`.
2. Execute available static checks, compile checks, dry-run checks, unit tests, or project-specific test commands.
3. Group results by:
   - `detail_design_verification`
   - `architecture_verification`
   - `requirement_acceptance`
4. Save `06_test_execution.md`.

If a test cannot be executed, mark it as `manual_required`, `environment_required`, or `not_configured`, and explain why.

Do not claim full closure if only detailed design/code verification is complete.

## Stage 7: Key Success Path

Trigger: the user confirms the result is acceptable and the workflow has enough evidence.

Actions:

1. Read all stage artifacts.
2. Summarize the reusable path.
3. Save `07_key_success_path.md`.
4. Save one durable memory record if a memory tool exists.

Do not save reusable success memory after every stage.

Final key path must include:

- task type
- requirement summary
- architecture summary
- detailed implementation path
- modified files and symbols
- used document evidence
- used code evidence
- generated artifacts
- test cases and execution results
- pitfalls
- next reuse hint

## Completion Rules

The workflow is complete only when:

- requirement review exists
- architecture review exists
- detailed design exists
- coding is implemented, unless the task is explicitly design-only
- test cases exist
- software verification results exist for all three levels, or skipped items are explicitly justified
- final key path exists

If any required stage is missing, report the current stage as incomplete and identify the next action.


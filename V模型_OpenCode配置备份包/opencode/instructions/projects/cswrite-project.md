# Project Profile: CSWrite Burner Software

This file contains project-specific configuration for the CSWrite / burner software project.

The global workflow is defined in:

```text
C:/Users/meigang90240/.config/opencode/instructions/vmodel-global.md
```

Keep this file focused on CSWrite-specific knowledge only.

## Project Identity

- Project name: CSWrite burner software
- Domain: chip programmer / burner / ICP / ISP / SWD software workflow
- Main code type: C and header files
- Primary current workspace:

```text
C:/Users/meigang90240/Desktop/KG/code/git_CSWrite3.0
```

When the current task mentions burner, 烧录器, CSWrite, chip support, ICP, ISP, SWD, chip config, or 8-bit/32-bit chip registration, use this project profile.

## Project MCP Tools

Use these MCP tools when available:

| Purpose | MCP name | Usage |
| --- | --- | --- |
| Reusable task memory | `taskpath_memory` | Search first for similar historical tasks; save only final key success paths |
| Document knowledge graph | `kg_rag_neo4j` | Search requirement documents, specs, protocol notes, and review evidence |
| Code knowledge graph | `codegraph` | Search code structure, files, symbols, dependencies, and reference implementations |

Recommended retrieval order:

1. `taskpath_memory.taskpath_search`
2. `kg_rag_neo4j.kg_hybrid_search`
3. `codegraph_get_curated_context` or the closest available codegraph context/search tool
4. Local file reads only after the tools narrow the scope

## Artifact Location

All workflow artifacts must be written into the current OpenCode workspace:

```text
./vmodel_runs/YYYYMMDD_HHMMSS_<task_slug>/
```

For the normal CSWrite workspace, this means:

```text
C:/Users/meigang90240/Desktop/KG/code/git_CSWrite3.0/vmodel_runs/YYYYMMDD_HHMMSS_<task_slug>/
```

This is required so the files appear in OpenCode's file list and Git changes panel.

## Test Case Skill

Use the OpenCode native Skill:

```text
eb-tool-test-case
```

Installed path:

```text
C:/Users/meigang90240/.config/opencode/skills/eb-tool-test-case
```

Fallback read path:

```text
C:/Users/meigang90240/.config/opencode/skills/eb-tool-test-case/SKILL.md
```

If the Skill is not visible after OpenCode restart, read the fallback `SKILL.md` as UTF-8 and follow its test-case formatting guidance.

## CSWrite Coding Scope

Prefer C/H code paths and project-local patterns.

Typical files and areas:

```text
src/common/config_8bit.h
src/common/cswrite_cfg_8bit.c
src/middlewave/program/chips/<CHIP>.c
src/middlewave/program/chips/*.h
```

For chip-support tasks, common implementation pattern:

1. Add or update chip macro and string macro in a config header.
2. Add or update chip implementation file under `src/middlewave/program/chips/`.
3. Register extern declaration, OPS macro, chip name list, and ops list in the config source file.
4. Keep chip name list and ops list synchronized.

For old ICP chip tasks:

- Prefer `io_icsp.h` and old ICP reference implementations.
- Do not silently use SPI or unrelated protocol code unless the requirements explicitly say so.

## Software Verification Policy

Hardware testing is not required for this project workflow unless the user explicitly asks for it.

Use available software checks:

- grep / Select-String checks
- static symbol existence checks
- compile/build checks when a build command is known
- dry-run consistency checks
- code review checks against detailed design

Test execution must still report three levels:

```text
detail_design_verification
architecture_verification
requirement_acceptance
```

If a real build or test command is not configured, mark it as `not_configured` and record the software evidence that was available.

## Project-Specific Final Memory

Only after the full workflow is accepted, save one reusable key path with `taskpath_memory.taskpath_save`.

The record should include:

- task type such as `add_chip_config`, `verify_existing_impl`, `modify_config_macro`, or `bug_fix`
- used documents
- used code files and symbols
- modified files
- test case file
- software checks run
- pitfalls
- next reuse hint


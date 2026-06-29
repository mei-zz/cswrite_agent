# Project Profile Template

Copy this file when adding a new project.

The global workflow lives in:

```text
C:/Users/meigang90240/.config/opencode/instructions/vmodel-global.md
```

Do not duplicate the global workflow here. Only write project-specific knowledge.

## Project Identity

- Project name:
- Domain:
- Main code type:
- Primary workspace:

```text
<absolute project workspace path>
```

Use this project profile when the current task mentions:

- `<keyword 1>`
- `<keyword 2>`
- `<keyword 3>`

## Project MCP Tools

| Purpose | MCP name | Usage |
| --- | --- | --- |
| Reusable task memory | `<memory_mcp>` | Search similar historical tasks; save final key success paths |
| Document knowledge | `<document_mcp>` | Search uploaded documents, specs, requirements, protocols, designs |
| Code knowledge | `<code_mcp>` | Search code files, symbols, dependencies, reference implementations |

Recommended retrieval order:

1. Memory MCP
2. Document MCP
3. Code MCP
4. Targeted local file reads

## Artifact Location

All artifacts must be written under the current workspace:

```text
./vmodel_runs/YYYYMMDD_HHMMSS_<task_slug>/
```

## Project Coding Scope

Typical files and modules:

```text
<path or module pattern>
```

Coding rules:

- Follow existing local style.
- Keep changes scoped to approved detailed design items.
- Do not refactor unrelated code.

## Project Test Policy

Hardware or external environment requirements:

- `<not required / required / optional>`

Available software checks:

- `<static check>`
- `<compile command>`
- `<unit test command>`
- `<dry-run command>`

Test execution must still report:

```text
detail_design_verification
architecture_verification
requirement_acceptance
```

## Final Memory

Only save final reusable memory after the complete workflow is accepted.

Required memory fields:

- task type
- used documents
- used code files and symbols
- modified files
- generated artifacts
- checks run
- pitfalls
- next reuse hint


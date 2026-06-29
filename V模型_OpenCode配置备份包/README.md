# V模型 OpenCode 配置备份包

该目录用于备份和迁移当前 OpenCode V 模型 Agent 配置。

## 包含内容

```text
opencode/
  opencode.current.local.jsonc   当前机器完整配置副本
  opencode.template.jsonc        给别人使用的路径占位符模板
  agents/
    vmodel.md                    全局 V 模型 Agent
    cswrite-vmodel.md            烧录器项目入口 Agent
  instructions/
    vmodel-global.md             全局 V 模型流程
    cswrite-vmodel.md            兼容旧引用的薄 instruction
    projects/
      cswrite-project.md         烧录器项目配置
      project-profile-template.md 新项目配置模板
  skills/
    eb-tool-test-case/           测试用例生成 Skill
mcp/
  .env.example
  scripts/
docs/
  OpenCode_V模型配置讲解.md
  V模型配置分层说明.md
```

## 使用方式

1. 将 `opencode/agents/` 复制到目标电脑：

```text
~/.config/opencode/agents/
```

2. 将 `opencode/instructions/` 复制到：

```text
~/.config/opencode/instructions/
```

3. 将 `opencode/skills/eb-tool-test-case/` 复制到：

```text
~/.config/opencode/skills/eb-tool-test-case/
```

4. 以 `opencode/opencode.template.jsonc` 为模板生成目标电脑的：

```text
~/.config/opencode/opencode.jsonc
```

5. 替换模板中的占位符：

```text
{{OPENCODE_HOME}}
{{BUNDLE_ROOT}}
{{KG_ROOT}}
{{CODE_REPO_ROOT}}
{{PYTHON_EXE}}
{{MODEL_BASE_URL}}
```

## 推荐阅读

先看：

```text
docs/OpenCode_V模型配置讲解.md
```

该文件说明每个配置文件的作用，以及如何给别人讲这套配置。


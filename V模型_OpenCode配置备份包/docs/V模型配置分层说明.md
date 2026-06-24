# V模型配置分层说明

## 目标

将原来混在一起的 OpenCode 配置拆成两层：

1. 全局 V 模型流程：任何软件研发项目都复用。
2. 项目级配置：只保存某个项目的代码库、知识库、MCP、Skill、检查命令和领域规则。

烧录器 / CSWrite 只是第一个项目示例。后续接入其他项目时，不需要改全局流程，只需要新增项目 profile。

## 当前文件结构

```text
C:/Users/meigang90240/.config/opencode/
  agents/
    vmodel.md                    全局 V 模型 Agent
    cswrite-vmodel.md            CSWrite 项目薄入口
  instructions/
    vmodel-global.md             全局 V 模型流程
    cswrite-vmodel.md            兼容旧引用的薄文件
    projects/
      cswrite-project.md         CSWrite / 烧录器项目配置
      project-profile-template.md 新项目配置模板
  opencode.jsonc                 只保留命令入口、MCP、模型配置
```

## 全局流程负责什么

`vmodel-global.md` 只定义通用流程：

- 当前工作区生成 `./vmodel_runs/<task>/`
- `00_context_pack.md`
- `01_requirement_review.md`
- `02_architecture_review.md`
- `03_detailed_design.md`
- `04_coding_record.md`
- `05_test_cases.md`
- `06_test_execution.md`
- `07_key_success_path.md`
- 需求和架构人工 Gate
- 用户修改文件后继续前必须读取
- 三层测试验证
- 最终只保存一次关键成功路径

## 项目配置负责什么

`projects/cswrite-project.md` 只定义 CSWrite 项目相关内容：

- 当前代码库路径
- 烧录器 / CSWrite / ICP / 芯片配置等关键词
- `taskpath_memory`
- `kg_rag_neo4j`
- `codegraph`
- `eb-tool-test-case`
- 典型 `.c/.h` 文件位置
- 旧 ICP 芯片实现注意事项
- 软件验证策略

## 当前命令

通用入口：

```text
/vmodel <任务>
```

CSWrite 项目入口：

```text
/cs-vmodel <任务>
```

两个命令都使用全局流程。`/cs-vmodel` 会额外强调使用 CSWrite 项目配置。

## 新增其他项目

1. 复制模板：

```text
C:/Users/meigang90240/.config/opencode/instructions/projects/project-profile-template.md
```

2. 改名，例如：

```text
C:/Users/meigang90240/.config/opencode/instructions/projects/<new-project>.md
```

3. 填写：

- 项目名称
- 工作区路径
- 关键词
- 文档 MCP
- 代码 MCP
- 记忆 MCP
- 测试 Skill 或测试命令
- 软件检查命令

4. 在 `opencode.jsonc` 的 `instructions` 中增加该项目 profile。

5. 可选：新增一个薄 Agent 和命令入口。

## 关键原则

- 不在项目配置里复制全局 V 模型流程。
- 不在全局流程里写烧录器细节。
- 每一步都必须在当前工作区生成可编辑 Markdown 文件。
- 用户修改 Markdown 后，Agent 必须读取修改后的文件再继续。
- 最终成功路径只在完整流程结束后保存一次。


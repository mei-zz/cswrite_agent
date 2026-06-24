# OpenCode V模型 Agent 配置讲解

## 1. 配置目标

当前 OpenCode 配置被拆成两层：

1. **全局 V 模型流程配置**：定义所有项目通用的研发流程。
2. **项目级配置**：定义某个具体项目的代码库、知识库、MCP、Skill、领域规则。

烧录器 / CSWrite 只是当前的一个项目示例。以后如果换成其他项目，不需要重写 V 模型流程，只需要新增一个项目级配置。

## 2. 总体文件结构

```text
C:/Users/meigang90240/.config/opencode/
  opencode.jsonc
  agents/
    vmodel.md
    cswrite-vmodel.md
    cswrite-vmodel.legacy-20260624_153245.md
    cswrite-rd.md
  instructions/
    vmodel-global.md
    cswrite-vmodel.md
    projects/
      cswrite-project.md
      project-profile-template.md
  skills/
    eb-tool-test-case/
```

## 3. opencode.jsonc

路径：

```text
C:/Users/meigang90240/.config/opencode/opencode.jsonc
```

作用：

- 指定 OpenCode 启动时加载哪些 instruction。
- 定义可用命令，例如 `/vmodel`、`/cs-vmodel`。
- 配置 MCP 服务，例如 `kg_rag_neo4j`、`codegraph`、`taskpath_memory`。
- 配置模型 provider。

当前只加载两个核心 instruction：

```json
"instructions": [
  "C:/Users/meigang90240/.config/opencode/instructions/vmodel-global.md",
  "C:/Users/meigang90240/.config/opencode/instructions/projects/cswrite-project.md"
]
```

这表示：

- `vmodel-global.md` 负责全局流程。
- `cswrite-project.md` 负责烧录器项目配置。

## 4. Agent 文件

### 4.1 vmodel.md

路径：

```text
C:/Users/meigang90240/.config/opencode/agents/vmodel.md
```

作用：

- 全局 V 模型 Agent。
- 不绑定烧录器。
- 后续其他项目也可以复用。

适用场景：

```text
用户想对任意项目执行 V 模型软件研发流程。
```

在 OpenCode 中对应命令：

```text
/vmodel
```

### 4.2 cswrite-vmodel.md

路径：

```text
C:/Users/meigang90240/.config/opencode/agents/cswrite-vmodel.md
```

作用：

- 烧录器 / CSWrite 项目的薄入口。
- 不保存完整流程，只声明使用：
  - `vmodel-global.md`
  - `projects/cswrite-project.md`

适用场景：

```text
用户要完成烧录器、CSWrite、芯片支持、ICP/ISP/SWD、烧录配置相关任务。
```

在 OpenCode 中应选择：

```text
Cswrite-Vmodel
```

对应命令：

```text
/cs-vmodel
```

### 4.3 cswrite-vmodel.legacy-*.md

路径示例：

```text
C:/Users/meigang90240/.config/opencode/agents/cswrite-vmodel.legacy-20260624_153245.md
```

作用：

- 旧版大配置备份。
- 仅用于回退或参考。
- 正常使用不要选择。

### 4.4 cswrite-rd.md

路径：

```text
C:/Users/meigang90240/.config/opencode/agents/cswrite-rd.md
```

作用：

- 早期研发流程 Agent。
- 不是完整 V 模型流程。
- 当前不建议用于新的烧录器任务。

## 5. 全局 V 模型流程配置

路径：

```text
C:/Users/meigang90240/.config/opencode/instructions/vmodel-global.md
```

作用：

定义所有项目通用的 V 模型软件研发流程。

它负责：

- 当前工作区生成阶段产物。
- 需求评审。
- 架构设计。
- 详细设计。
- 编码记录。
- 测试用例生成。
- 测试执行记录。
- 最终关键成功路径沉淀。
- 人工确认 Gate。
- 用户修改文档后继续前必须重新读取。
- 三层验证：
  - `detail_design_verification`
  - `architecture_verification`
  - `requirement_acceptance`

它不负责：

- 具体项目的代码库路径。
- 具体项目使用哪个 MCP。
- 具体项目有哪些领域词。
- 具体项目如何写测试用例。
- 烧录器、芯片、ICP 等项目知识。

这些都放在项目级配置中。

## 6. 烧录器项目级配置

路径：

```text
C:/Users/meigang90240/.config/opencode/instructions/projects/cswrite-project.md
```

作用：

定义烧录器 / CSWrite 项目的专用信息。

它负责：

- 项目名称：CSWrite burner software。
- 当前代码库路径：

```text
C:/Users/meigang90240/Desktop/KG/code/git_CSWrite3.0
```

- 触发关键词：
  - 烧录器
  - CSWrite
  - chip support
  - ICP
  - ISP
  - SWD
  - chip config
  - 8-bit / 32-bit chip registration

- MCP 使用规则：
  - `taskpath_memory`
  - `kg_rag_neo4j`
  - `codegraph`

- 测试用例 Skill：

```text
eb-tool-test-case
```

- 常见代码路径：

```text
src/common/config_8bit.h
src/common/cswrite_cfg_8bit.c
src/middlewave/program/chips/<CHIP>.c
src/middlewave/program/chips/*.h
```

- 旧 ICP 芯片任务规则：
  - 优先使用 `io_icsp.h`
  - 不要误用 SPI 协议
  - 芯片名称列表和 ops 列表要同步

- 软件验证策略：
  - 不要求硬件测试
  - 使用静态检查、grep、dry-run、编译检查等软件侧证据

## 7. 项目模板

路径：

```text
C:/Users/meigang90240/.config/opencode/instructions/projects/project-profile-template.md
```

作用：

- 新项目接入模板。
- 后续如果接入其他项目，复制这个文件，然后改成新项目配置。

新增项目时需要填写：

- 项目名称
- 工作区路径
- 项目关键词
- 文档知识库 MCP
- 代码知识库 MCP
- 记忆 MCP
- 测试 Skill 或测试命令
- 软件检查命令
- 项目编码规则

## 8. MCP 配置

MCP 配置位于：

```text
C:/Users/meigang90240/.config/opencode/opencode.jsonc
```

当前主要 MCP：

| MCP | 类型 | 作用 |
| --- | --- | --- |
| `kg_rag_neo4j` | local | 查询 Neo4j 文档知识图谱 |
| `codegraph` | local | 查询代码结构、符号、依赖、参考实现 |
| `taskpath_memory` | local | 检索历史成功路径，最终保存关键路径 |
| `maxkb` | remote | 旧的 MaxKB 知识库接口，目前不是 V 模型主流程核心 |

### 8.1 kg_rag_neo4j

作用：

- 检索需求文档、协议文档、设计资料、测试资料。
- 作为需求理解和架构设计的文档依据。

当前启动方式：

```json
"kg_rag_neo4j": {
  "type": "local",
  "enabled": true,
  "cwd": "C:/Users/meigang90240/Desktop/KG",
  "command": [
    "D:/anaconda3/python.exe",
    "C:/Users/meigang90240/Desktop/KG/scripts/kg_rag_mcp_server.py"
  ],
  "timeout": 180000
}
```

### 8.2 codegraph

作用：

- 检索代码库中的 `.c`、`.h` 文件。
- 查询函数、宏、结构体、依赖、调用关系。
- 帮助 Agent 找到应该参考哪些代码。

当前启动方式：

```json
"codegraph": {
  "type": "local",
  "enabled": true,
  "cwd": "C:/Users/meigang90240/Desktop/KG/code/git_CSWrite3.0",
  "command": [
    "powershell.exe",
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    "C:/Users/meigang90240/Desktop/KG/scripts/start_codegraph_cswrite.ps1"
  ]
}
```

### 8.3 taskpath_memory

作用：

- 检索历史任务成功路径。
- 最终流程完成后保存一条关键成功路径。
- 避免每次都重新学习项目。

当前启动方式：

```json
"taskpath_memory": {
  "type": "local",
  "enabled": true,
  "cwd": "C:/Users/meigang90240/Desktop/KG",
  "command": [
    "D:/anaconda3/python.exe",
    "C:/Users/meigang90240/Desktop/KG/scripts/taskpath_memory_mcp_proxy.py"
  ],
  "timeout": 180000
}
```

## 9. Skill 配置

当前测试用例 Skill：

```text
C:/Users/meigang90240/.config/opencode/skills/eb-tool-test-case
```

作用：

- 指导 Agent 如何生成测试用例文档。
- 当前在烧录器项目中用于生成 `05_test_cases.md`。

如果 OpenCode 没有自动识别 Skill，则项目配置要求兜底读取：

```text
C:/Users/meigang90240/.config/opencode/skills/eb-tool-test-case/SKILL.md
```

## 10. 命令入口

当前 `opencode.jsonc` 中有两个命令：

| 命令 | Agent | 使用场景 |
| --- | --- | --- |
| `/vmodel` | `vmodel` | 任意项目的通用 V 模型流程 |
| `/cs-vmodel` | `cswrite-vmodel` | 烧录器 / CSWrite 项目任务 |

烧录器任务建议使用：

```text
/cs-vmodel 新增 8 位旧 ICP 芯片 VMODEL_TEST_8BIT，先只做需求理解和需求评审
```

或者在 OpenCode 桌面端直接选择：

```text
Cswrite-Vmodel
```

## 11. 阶段产物

所有阶段产物必须写在当前 OpenCode 工作区：

```text
./vmodel_runs/YYYYMMDD_HHMMSS_<task_slug>/
```

文件包括：

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

这些文件会显示在 OpenCode 的文件列表和 Git changes 中。

用户可以编辑：

- 需求文档
- 架构文档
- 详细设计文档
- 测试用例文档
- 测试执行记录

然后要求 Agent 继续下一步。Agent 必须先读取用户修改后的文件。

## 12. 正常烧录器任务操作流程

### 第一步：选择 Agent

在 OpenCode 中选择：

```text
Cswrite-Vmodel
```

不要选择：

- `Cswrite-Rd`
- `Cswrite-Vmodel.Legacy`
- `Plan`

### 第二步：提出需求

示例：

```text
新增 8 位旧 ICP 芯片 VMODEL_TEST_8BIT。先只做需求理解和需求评审，生成需求评审文档到当前工作区，不要进入架构设计，不要写代码。
```

期望生成：

```text
vmodel_runs/<task>/01_requirement_review.md
```

### 第三步：修改并确认需求

用户可以直接修改 `01_requirement_review.md`。

然后输入：

```text
我已修改并确认 01_requirement_review.md，请读取该文件，继续生成架构设计文档，不要进入详细设计，不要写代码。
```

### 第四步：修改并确认架构

期望生成：

```text
vmodel_runs/<task>/02_architecture_review.md
```

用户修改后继续：

```text
我已修改并确认 02_architecture_review.md，请读取该文件，继续生成详细设计文档。
```

### 第五步：详细设计和编码

期望生成：

```text
vmodel_runs/<task>/03_detailed_design.md
```

确认后再要求编码：

```text
我已确认 03_detailed_design.md，请按照详细设计执行代码修改，并生成编码记录。
```

期望生成：

```text
vmodel_runs/<task>/04_coding_record.md
```

### 第六步：测试用例

```text
请基于已确认需求、架构、详细设计和编码记录生成测试用例文档。
```

期望生成：

```text
vmodel_runs/<task>/05_test_cases.md
```

### 第七步：测试执行记录

```text
请执行当前可用的软件检查，并生成测试执行报告。无需硬件测试。
```

期望生成：

```text
vmodel_runs/<task>/06_test_execution.md
```

### 第八步：保存关键成功路径

```text
我接受当前结果，请生成最终关键成功路径并保存为可复用记忆。
```

期望生成：

```text
vmodel_runs/<task>/07_key_success_path.md
```

并通过 `taskpath_memory` 保存最终成功路径。

## 13. 如何接入新项目

1. 复制模板：

```text
C:/Users/meigang90240/.config/opencode/instructions/projects/project-profile-template.md
```

2. 改名，例如：

```text
C:/Users/meigang90240/.config/opencode/instructions/projects/my-project.md
```

3. 填写新项目的：

- 工作区路径
- 关键词
- 文档 MCP
- 代码 MCP
- 记忆 MCP
- 测试规则
- 编码范围
- 检查命令

4. 在 `opencode.jsonc` 的 `instructions` 中加入新项目 profile。

5. 可选：新增一个薄 Agent 和命令入口。

## 14. 讲解时的核心表达

可以这样对别人解释：

> 我们把 Agent 配置拆成了全局流程和项目配置两层。全局流程负责 V 模型的阶段推进、人工确认、阶段文档、测试验证和成功路径沉淀；项目配置负责告诉 Agent 当前项目有哪些知识库、代码库、MCP、Skill 和领域规则。烧录器只是一个项目 profile，后续其他项目只需要新增 profile，不需要重写流程。


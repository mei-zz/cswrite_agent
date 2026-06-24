# CSWrite LangGraph 研发 Agent

这个工程把当前 OpenCode 中已经跑通的烧录器研发流程迁移成 LangGraph 实现。

核心能力：

- 复用现有 MCP：`taskpath_memory`、`kg_rag_neo4j`、`codegraph`
- 支持 Human in the loop：需求评审和架构评审必须人工确认
- 支持 SQLite 记忆库：保存运行状态、阶段事件、最终关键成功路径
- 支持完整研发闭环：需求理解、架构设计、详细设计、编码、测试用例、测试执行、关键路径沉淀
- 支持三层验证：编码/详细设计验证、架构验证、需求验收
- 支持 demo/real 两种模式：demo 不修改真实仓库，real 接入真实 MCP 和代码库

## 目录结构

```text
src/cswrite_langgraph_agent/
  config.py        配置与环境变量
  state.py         LangGraph 状态定义
  graph.py         LangGraph 状态机
  agents.py        各阶段 Agent 节点
  mcp_adapter.py   MCP stdio 客户端和检索适配
  memory.py        SQLite 记忆管理
  llm.py           百炼模型调用封装
  cli.py           命令行入口
examples/
  fake_cswrite_repo/ 端到端测试用示例代码库
  fake_docs/         端到端测试用示例文档
tests/
  run_step_tests.py  分步测试脚本
```

## 快速测试

在本目录执行：

```powershell
D:/anaconda3/python.exe -m pip install -r requirements.txt
$env:PYTHONPATH="src"
D:/anaconda3/python.exe tests/run_step_tests.py
```

## 运行一次完整 demo

```powershell
$env:PYTHONPATH="src"
D:/anaconda3/python.exe -m cswrite_langgraph_agent.cli run `
  --task "新增一个测试用 8 位旧 ICP 芯片 VMODEL_TEST_8BIT" `
  --mode demo `
  --llm-mode template `
  --auto-approve `
  --execute-code
```

运行后会生成：

```text
runs/YYYYMMDD_HHMMSS_<task>/
  00_context_pack.md
  01_requirement_review.md
  02_architecture_review.md
  03_detailed_design.md
  04_coding_record.md
  05_test_cases.md
  06_test_execution.md
  07_key_success_path.md
  state_latest.json
```

## 人工确认模式

先运行到需求评审：

```powershell
$env:PYTHONPATH="src"
D:/anaconda3/python.exe -m cswrite_langgraph_agent.cli run `
  --task "新增 DMA 模块支持，先做需求确认" `
  --mode demo
```

检查 `01_requirement_review.md` 后继续：

```powershell
D:/anaconda3/python.exe -m cswrite_langgraph_agent.cli resume `
  --run-id <run_id> `
  --gate requirement
```

架构评审后继续：

```powershell
D:/anaconda3/python.exe -m cswrite_langgraph_agent.cli resume `
  --run-id <run_id> `
  --gate architecture `
  --auto-approve-rest
```

## 真实模式

真实模式会复用你已有的 MCP 启动命令：

- 文档图谱：`C:/Users/meigang90240/Desktop/KG/scripts/kg_rag_mcp_server.py`
- 代码图谱：`C:/Users/meigang90240/Desktop/KG/scripts/start_codegraph_cswrite.ps1`
- TaskPath：`C:/Users/meigang90240/Desktop/KG/scripts/taskpath_memory_mcp_proxy.py`

```powershell
$env:PYTHONPATH="src"
D:/anaconda3/python.exe -m cswrite_langgraph_agent.cli run `
  --task "新增某芯片支持，先进行需求评审" `
  --mode real `
  --llm-mode bailian
```

建议真实模式先不要加 `--execute-code`，确认详细设计无误后再开启代码修改。

真实 codegraph 检索建议在任务里附带关键代码符号，例如：

```text
config_8bit cswrite_cfg_8bit io_icsp chip_operation
```

这样可以降低中文 query 在 WSL/codegraph 日志中编码显示异常带来的检索不稳定。

## 百炼模型

`.env.example` 中保留了百炼配置。当前工程会自动读取：

- 本工程 `.env`
- `C:/Users/meigang90240/Desktop/KG/.env`

模型冒烟测试：

```powershell
$env:PYTHONPATH="src"
D:/anaconda3/python.exe -m cswrite_langgraph_agent.cli llm-smoke
```

## 已完成测试

详细记录见：

```text
docs/测试记录.md
```

已通过：

- Python 编译检查
- CLI 环境检查
- Human in the loop 暂停
- 自动确认端到端 demo
- 百炼参与全流程 demo：6 个核心阶段均真实调用模型
- 示例代码真实修改
- 三层测试用例生成
- 三层测试执行报告
- SQLite 成功路径记忆
- 失败任务不写入成功路径记忆
- 百炼模型冒烟测试
- 真实 MCP 检索适配测试

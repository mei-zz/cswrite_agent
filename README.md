# CSWrite LangGraph 研发 Agent

这个工程把当前 OpenCode 中已经跑通的烧录器研发流程迁移成 LangGraph 实现。

核心能力：

- 支持任务结构化解析：从自然语言任务中提取芯片宏、位宽、协议、目标文件和 ops 符号
- 支持 Planner：根据任务复杂度制定执行计划、自修复预算和条件节点策略
- 支持受控上下文管理：对检索结果做证据选择、预算控制、覆盖度统计和冲突提示
- 复用现有 MCP：`taskpath_memory`、`kg_rag_neo4j`、`codegraph`
- 支持 Human in the loop：需求评审和架构评审必须人工确认
- 支持 SQLite 分层记忆库：保存 episodic/semantic/procedural/negative 四类记忆
- 支持完整研发闭环：需求理解、架构设计、详细设计、编码、测试用例、测试执行、关键路径沉淀
- 支持三层验证：编码/详细设计验证、架构验证、需求验收
- 支持 Critic / Reflection：测试失败后检查跨阶段矛盾，自动决定回退到详细设计、编码或测试设计
- 支持自修复路径：失败不直接 closed，优先回退修复并重新测试，达到修复次数上限才失败闭环
- 支持 V 模型追溯矩阵：需求、架构、详细设计、代码和测试结果可回溯
- 支持可观测性报告：节点耗时、LLM 调用、上下文覆盖、记忆计数和错误集中展示
- 支持 demo/real 两种模式：demo 不修改真实仓库，real 接入真实 MCP 和代码库

## 目录结构

```text
src/cswrite_langgraph_agent/
  config.py        配置与环境变量
  state.py         LangGraph 状态定义
  graph.py         LangGraph 状态机
  agents.py        各阶段 Agent 节点
  mcp_adapter.py   MCP stdio 客户端和检索适配
  context_manager.py 上下文预算、证据选择和覆盖度统计
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
  --task "新增一个测试用 8 位旧 ICP 芯片 VMODEL_INTERVIEW_8BIT" `
  --mode demo `
  --llm-mode template `
  --auto-approve `
  --execute-code
```

运行后会生成：

```text
runs/YYYYMMDD_HHMMSS_<task>/
  00_task_analysis.md
  00_planner.md
  00_context_pack.md
  00_managed_context.md
  01_requirement_review.md
  02_architecture_review.md
  03_detailed_design.md
  04_coding_record.md
  05_test_cases.md
  06_test_execution.md
  10_critic_report.md
  11_reflection_attempt_1.md        # 仅触发自修复时生成
  07_key_success_path.md
  08_traceability_matrix.md
  09_observability_report.md
  state_latest.json
```

## 导出 LangGraph 状态图

```powershell
$env:PYTHONPATH="src"
D:/anaconda3/python.exe -m cswrite_langgraph_agent.cli graph --output docs/langgraph_flow.mmd
```

`docs/langgraph_flow.mmd` 可用于面试讲解状态机、条件边、人工 Gate 和恢复入口。

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

真实百炼参与完整流程：

```powershell
$env:PYTHONPATH="src"
D:/anaconda3/python.exe -m cswrite_langgraph_agent.cli run `
  --task "新增一个测试用 8 位旧 ICP 芯片 VMODEL_BAILIAN_SHOWCASE_8BIT，验证完整研发流程" `
  --mode demo `
  --llm-mode bailian `
  --auto-approve `
  --execute-code
```

运行后可在 `state_latest.json` 中查看 `llm_calls`，每个核心阶段都会记录真实模型调用结果。

## 演示自修复

下面命令会在首轮编码故意漏写注册表项，测试失败后由 Critic/Reflection 自动回退到 `coding` 修复，再重新测试：

```powershell
$env:PYTHONPATH="src"
D:/anaconda3/python.exe -m cswrite_langgraph_agent.cli run `
  --task "新增一个测试用 8 位旧 ICP 芯片 VMODEL_REPAIR_8BIT，验证自修复流程" `
  --mode demo `
  --llm-mode bailian `
  --auto-approve `
  --execute-code `
  --inject-coding-defect `
  --max-repair-attempts 1
```

## 面试演示文档

```text
docs/面试演示指南.md
docs/langgraph_flow.mmd
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

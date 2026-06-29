# Agent 观测报告：只做设计不执行编码的旧 ICP 芯片任务

## 总览

```json
{
  "run_id": "20260629_172913_261",
  "task": "只做设计不执行编码的旧 ICP 芯片任务",
  "total_elapsed_ms_before_report": 32.04,
  "node_count_before_report": 14,
  "artifact_count": 12,
  "llm": {
    "mode": "template",
    "calls": 0,
    "ok": 0,
    "failed": 0
  },
  "retrieval": {
    "diagnostics": [
      "demo 模式：使用 examples/fake_docs 与示例仓库检索。"
    ],
    "doc_hit_type": "list",
    "code_hit_type": "list",
    "memory_hits": 6
  },
  "context": {
    "selected_count": 13,
    "coverage": {
      "required_keywords": [
        "VMODEL_TEST_8BIT",
        "STR_VMODEL_TEST_8BIT",
        "OPS_VMODEL_TEST_8BIT",
        "src/common/config_8bit.h",
        "src/common/cswrite_cfg_8bit.c",
        "io_icsp",
        "chip_operation",
        "旧 ICP"
      ],
      "hit_keywords": [
        "VMODEL_TEST_8BIT",
        "STR_VMODEL_TEST_8BIT",
        "OPS_VMODEL_TEST_8BIT",
        "src/common/config_8bit.h",
        "src/common/cswrite_cfg_8bit.c",
        "io_icsp",
        "chip_operation",
        "旧 ICP"
      ],
      "missed_keywords": [],
      "coverage_ratio": 1.0
    },
    "conflicts": []
  },
  "traceability": {
    "complete": false,
    "gap_count": 2
  },
  "memory_counts_before_close": {
    "episodic": 2,
    "procedural": 2,
    "semantic": 2
  },
  "errors": []
}
```

## 节点运行统计

| node | stage | elapsed_ms | artifact_count | llm_call_count | error_count |
| --- | --- | --- | --- | --- | --- |
| init_run | init | 11.84 | 0 | 0 | 0 |
| task_analysis | task_analysis | 1.31 | 1 | 0 | 0 |
| planner | planner | 0.89 | 2 | 0 | 0 |
| retrieval | retrieval | 6.2 | 4 | 0 | 0 |
| requirement_review | requirement_review | 0.87 | 5 | 0 | 0 |
| requirement_gate | requirement_review | 0.0 | 5 | 0 | 0 |
| architecture_review | architecture_review | 0.86 | 6 | 0 | 0 |
| architecture_gate | architecture_review | 0.0 | 6 | 0 | 0 |
| detailed_design | detailed_design | 0.92 | 7 | 0 | 0 |
| coding | coding | 1.14 | 8 | 0 | 0 |
| test_design | test_design | 1.93 | 9 | 0 | 0 |
| test_execution | test_execution | 3.26 | 10 | 0 | 0 |
| critic | critic | 1.51 | 11 | 0 | 0 |
| traceability_matrix | traceability_matrix | 1.31 | 12 | 0 | 0 |

## LLM 调用统计

- 无

## 检索与上下文管理

- 记忆命中数：6
- 上下文入选证据数：13
- 关键约束覆盖率：1.0
- 上下文冲突数：0

## 记忆库分层计数

```json
{
  "episodic": 2,
  "procedural": 2,
  "semantic": 2
}
```
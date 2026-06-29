# Agent 观测报告：新增一个测试用 8 位旧 ICP 芯片 VMODEL_TEST_8BIT，验证完整研发流程

## 总览

```json
{
  "run_id": "20260629_172912_557",
  "task": "新增一个测试用 8 位旧 ICP 芯片 VMODEL_TEST_8BIT，验证完整研发流程",
  "total_elapsed_ms_before_report": 31.37,
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
    "memory_hits": 0
  },
  "context": {
    "selected_count": 7,
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
        "io_icsp",
        "chip_operation",
        "旧 ICP"
      ],
      "missed_keywords": [
        "STR_VMODEL_TEST_8BIT",
        "OPS_VMODEL_TEST_8BIT",
        "src/common/config_8bit.h",
        "src/common/cswrite_cfg_8bit.c"
      ],
      "coverage_ratio": 0.5
    },
    "conflicts": []
  },
  "traceability": {
    "complete": true,
    "gap_count": 0
  },
  "memory_counts_before_close": {},
  "errors": []
}
```

## 节点运行统计

| node | stage | elapsed_ms | artifact_count | llm_call_count | error_count |
| --- | --- | --- | --- | --- | --- |
| init_run | init | 8.77 | 0 | 0 | 0 |
| task_analysis | task_analysis | 1.5 | 1 | 0 | 0 |
| planner | planner | 1.07 | 2 | 0 | 0 |
| retrieval | retrieval | 5.21 | 4 | 0 | 0 |
| requirement_review | requirement_review | 1.2 | 5 | 0 | 0 |
| requirement_gate | requirement_review | 0.0 | 5 | 0 | 0 |
| architecture_review | architecture_review | 0.83 | 6 | 0 | 0 |
| architecture_gate | architecture_review | 0.0 | 6 | 0 | 0 |
| detailed_design | detailed_design | 0.86 | 7 | 0 | 0 |
| coding | coding | 6.35 | 8 | 0 | 0 |
| test_design | test_design | 1.31 | 9 | 0 | 0 |
| test_execution | test_execution | 2.5 | 10 | 0 | 0 |
| critic | critic | 0.86 | 11 | 0 | 0 |
| traceability_matrix | traceability_matrix | 0.91 | 12 | 0 | 0 |

## LLM 调用统计

- 无

## 检索与上下文管理

- 记忆命中数：0
- 上下文入选证据数：7
- 关键约束覆盖率：0.5
- 上下文冲突数：0

## 记忆库分层计数

```json
{}
```
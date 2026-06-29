# Agent 观测报告：新增一个测试用 8 位旧 ICP 芯片 VMODEL_REPAIR_8BIT，验证自修复流程

## 总览

```json
{
  "run_id": "20260629_172912_862",
  "task": "新增一个测试用 8 位旧 ICP 芯片 VMODEL_REPAIR_8BIT，验证自修复流程",
  "total_elapsed_ms_before_report": 41.92,
  "node_count_before_report": 19,
  "artifact_count": 13,
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
    "memory_hits": 3
  },
  "context": {
    "selected_count": 10,
    "coverage": {
      "required_keywords": [
        "VMODEL_REPAIR_8BIT",
        "STR_VMODEL_REPAIR_8BIT",
        "OPS_VMODEL_REPAIR_8BIT",
        "src/common/config_8bit.h",
        "src/common/cswrite_cfg_8bit.c",
        "io_icsp",
        "chip_operation",
        "旧 ICP"
      ],
      "hit_keywords": [
        "VMODEL_REPAIR_8BIT",
        "src/common/config_8bit.h",
        "src/common/cswrite_cfg_8bit.c",
        "io_icsp",
        "chip_operation",
        "旧 ICP"
      ],
      "missed_keywords": [
        "STR_VMODEL_REPAIR_8BIT",
        "OPS_VMODEL_REPAIR_8BIT"
      ],
      "coverage_ratio": 0.75
    },
    "conflicts": []
  },
  "traceability": {
    "complete": true,
    "gap_count": 0
  },
  "memory_counts_before_close": {
    "episodic": 1,
    "procedural": 1,
    "semantic": 1
  },
  "errors": []
}
```

## 节点运行统计

| node | stage | elapsed_ms | artifact_count | llm_call_count | error_count |
| --- | --- | --- | --- | --- | --- |
| init_run | init | 9.25 | 0 | 0 | 0 |
| task_analysis | task_analysis | 1.54 | 1 | 0 | 0 |
| planner | planner | 0.94 | 2 | 0 | 0 |
| retrieval | retrieval | 6.53 | 4 | 0 | 0 |
| requirement_review | requirement_review | 1.33 | 5 | 0 | 0 |
| requirement_gate | requirement_review | 0.0 | 5 | 0 | 0 |
| architecture_review | architecture_review | 0.88 | 6 | 0 | 0 |
| architecture_gate | architecture_review | 0.01 | 6 | 0 | 0 |
| detailed_design | detailed_design | 1.25 | 7 | 0 | 0 |
| coding | coding | 3.49 | 8 | 0 | 0 |
| test_design | test_design | 1.31 | 9 | 0 | 0 |
| test_execution | test_execution | 2.74 | 10 | 0 | 0 |
| critic | critic | 0.93 | 11 | 0 | 0 |
| reflection | reflection | 0.86 | 12 | 0 | 0 |
| coding | coding | 5.54 | 12 | 0 | 0 |
| test_design | test_design | 1.14 | 12 | 0 | 0 |
| test_execution | test_execution | 2.35 | 12 | 0 | 0 |
| critic | critic | 0.78 | 12 | 0 | 0 |
| traceability_matrix | traceability_matrix | 1.05 | 13 | 0 | 0 |

## LLM 调用统计

- 无

## 检索与上下文管理

- 记忆命中数：3
- 上下文入选证据数：10
- 关键约束覆盖率：0.75
- 上下文冲突数：0

## 记忆库分层计数

```json
{
  "episodic": 1,
  "procedural": 1,
  "semantic": 1
}
```
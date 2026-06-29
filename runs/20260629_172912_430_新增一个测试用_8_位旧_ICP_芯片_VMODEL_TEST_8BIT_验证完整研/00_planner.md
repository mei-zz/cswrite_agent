# Planner 执行计划：新增一个测试用 8 位旧 ICP 芯片 VMODEL_TEST_8BIT，验证完整研发流程

## 计划 JSON

```json
{
  "complexity_score": 2,
  "complexity_level": "low",
  "complexity_reasons": [
    "任务要求完整闭环或成熟 Agent 能力"
  ],
  "mandatory_nodes": [
    "task_analysis",
    "retrieval",
    "requirement_review",
    "architecture_review",
    "detailed_design",
    "test_design",
    "test_execution",
    "critic",
    "traceability_matrix",
    "observability",
    "closed"
  ],
  "conditional_nodes": {
    "coding": false,
    "reflection": false,
    "human_gates": true
  },
  "repair_policy": {
    "enabled": false,
    "max_repair_attempts": 0,
    "preferred_order": [
      "coding",
      "detailed_design"
    ],
    "stop_rule": "达到最大修复次数或 Critic 判定无可自动修复动作后进入闭环失败总结。"
  }
}
```

## 大模型阶段判断

- 未启用大模型模式
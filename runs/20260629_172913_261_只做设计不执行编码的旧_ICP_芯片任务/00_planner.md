# Planner 执行计划：只做设计不执行编码的旧 ICP 芯片任务

## 计划 JSON

```json
{
  "complexity_score": 1,
  "complexity_level": "low",
  "complexity_reasons": [
    "标准 8 位旧 ICP 新芯片接入"
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
    "human_gates": false
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
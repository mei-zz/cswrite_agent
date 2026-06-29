# Planner 执行计划：新增一个测试用 8 位旧 ICP 芯片 VMODEL_SELF_REPAIR_FINAL_8BIT，验证 Planner Critic Reflection 自修复流程

## 计划 JSON

```json
{
  "complexity_score": 4,
  "complexity_level": "medium",
  "complexity_reasons": [
    "开启代码修改，需要测试失败后的修复路径",
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
    "coding": true,
    "reflection": true,
    "human_gates": false
  },
  "repair_policy": {
    "enabled": true,
    "max_repair_attempts": 1,
    "preferred_order": [
      "coding",
      "detailed_design"
    ],
    "stop_rule": "达到最大修复次数或 Critic 判定无可自动修复动作后进入闭环失败总结。"
  }
}
```

## 大模型阶段判断

**总体结论**
计划框架合理，但针对“验证自修复”的核心目标，参数配置与测试边界存在明显风险。

**为什么需要自修复**
**必须需要**。本任务的根本目的是“验证自修复流程”而非单纯“新增芯片”。若不开启自修复，任务将失去核心验证价值。计划中已正确配置 `repair_policy.enabled: true` 及 `reflection: true`，方向正确。

**判断依据与风险**
1. **修复次数上限过低（风险）**：`max_repair_attempts: 1`。仅 1 次修复难以充分验证 Critic 反馈与 Reflection 的多轮迭代能力。若首次修复失败即终止，无法评估 Agent 的深层纠错逻辑。
2. **测试环境脱离真实硬件（风险）**：`scope_note` 表明真实硬件烧录延后。若 `test_execution` 仅依赖编译或 Mock 测试，可能无法暴露旧 ICP 协议特有的时序/指令错误，导致自修复流程“无错可修”或陷入无效修复。
3. **旧 ICP 协议特性（依据）**：旧 ICP 时序严格，直接复用参考芯片（CSU32PX10）参数极易报错。这是触发修复的良好契机，但需确保测试用例能精准捕获此类底层协议错误。

**下一步**
1. **调整修复参数**：将 `max_repair_attempts` 提升至 2~3 次，确保能完整跑通“失败-反思-再修复”的闭环。
2. **构造确定性失败用例**：在 `test_design` 中故意埋入旧 ICP 典型错误（如时序参数越界、缺失旧协议特有宏），确保 `test_execution` 必定失败，强制触发修复流程。
3. **增加 Critic 防作弊规则**：在 `critic` 节点增加校验，严禁 Agent 通过“修改测试用例预期”或“降级协议标准”来通过测试，必须从 `coding` 或 `detailed_design` 层面修复根因。
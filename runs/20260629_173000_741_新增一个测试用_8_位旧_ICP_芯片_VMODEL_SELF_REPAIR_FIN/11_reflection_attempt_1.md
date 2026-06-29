# Reflection 修复决策：新增一个测试用 8 位旧 ICP 芯片 VMODEL_SELF_REPAIR_FINAL_8BIT，验证 Planner Critic Reflection 自修复流程

## 修复决策

```json
{
  "attempt": 1,
  "reason": "Critic 发现需求、设计、代码或测试之间存在不一致。",
  "critic_status": "fail",
  "critic_issue_count": 5,
  "next_node": "coding",
  "repair_actions": [
    "重新执行编码节点，补齐缺失的宏、芯片实现或注册表项。",
    "保留详细设计不变，优先修复代码事实与设计之间的缺口。"
  ]
}
```

## 大模型阶段判断

**失败原因（判断依据）**
代码实现与设计/需求存在严重不一致，且包含注入缺陷：
1. **关键宏缺失**：`cswrite_cfg_8bit.c` 遗漏了 `OPS_VMODEL_SELF_REPAIR_FINAL_8BIT` 和 `STR_VMODEL_SELF_REPAIR_FINAL_8BIT` 宏。
2. **设计验证失败**：代码未完全落实详细设计（DD3）与架构验证（A1-A3）。
3. **状态与需求不达标**：当前编码状态为含注入缺陷（`implemented_with_injected_defect`），且仅通过 demo 静态检查，未满足真实烧录需求（R1）。

**风险**
1. **硬件执行失效**：缺失核心宏与配置将导致 8bit 烧录或自修复链路在真实芯片上运行崩溃。
2. **质量失控**：携带注入缺陷的代码若流入后续环节，将引发严重的测试或生产事故。

**下一步动作（回退至 Coding 节点）**
1. **补齐代码缺口**：在 `cswrite_cfg_8bit.c` 中补充缺失的宏定义、芯片实现及注册表项。
2. **清除注入缺陷**：修复代码已知缺陷，将编码状态恢复为正常实现。
3. **冻结设计对齐代码**：保持详细设计不变，严格修改代码以匹配设计事实，完成后重新提交验证。
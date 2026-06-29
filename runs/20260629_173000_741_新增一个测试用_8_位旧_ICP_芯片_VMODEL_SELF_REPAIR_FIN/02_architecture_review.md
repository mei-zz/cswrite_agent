# 架构设计评审：新增一个测试用 8 位旧 ICP 芯片 VMODEL_SELF_REPAIR_FINAL_8BIT，验证 Planner Critic Reflection 自修复流程

| arch_id | linked_requirement | layer_module | design_decision | interface_dependency | user_confirmation | status |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | R1 | 芯片编译宏与名称层 | 在 src/common/config_8bit.h 新增 VMODEL_SELF_REPAIR_FINAL_8BIT 和 STR_VMODEL_SELF_REPAIR_FINAL_8BIT。 | 被 src/common/cswrite_cfg_8bit.c 和 UI/配置层引用。 | pending | pending_user_review |
| A2 | R1,R2 | 芯片操作实现层 | 新增 src/middlewave/program/chips/VMODEL_SELF_REPAIR_FINAL_8BIT.c，按 chip_operation 回调模板实现。 | 依赖 io_icsp.h 的 旧 ICP 通信接口。 | pending | pending_user_review |
| A3 | R1,R3 | 注册与调度层 | 在 src/common/cswrite_cfg_8bit.c 注册 extern、OPS_VMODEL_SELF_REPAIR_FINAL_8BIT、名称列表和 ops 列表。 | 名称列表与 ops 列表索引必须一致。 | pending | pending_user_review |

## 大模型阶段判断

**【总体判断】**
基本能支撑，但存在关键细节隐患与闭环缺失。

**【判断依据】**
设计覆盖了宏定义(A1)、底层实现(A2)、注册调度(A3)三个核心层级，符合嵌入式烧录器新增芯片支持的标准分层架构。

**【核心风险】**
1. **接口兼容性风险**：A2 依赖“旧 ICP 通信接口”，旧接口的时序、电压或协议可能无法完全满足新芯片（特别是带 Self-Repair 特性）的特殊需求。
2. **数组错位风险**：A3 中名称列表与 ops 列表强依赖索引一致，手动添加极易发生错位，导致烧录错芯片或系统崩溃。
3. **架构闭环缺失**：A1 提到被“UI/配置层引用”，但当前架构中未见 UI 层（如界面下拉框、配置文件解析）的具体适配设计。

**【最需要人工确认的点】**
1. **旧接口兼容性**：`io_icsp.h` 的旧 ICP 协议/时序是否 100% 兼容该 8BIT 芯片的 Self-Repair 烧录/修复流程？是否需要特殊的延时或电平翻转？
2. **索引严格对齐**：A3 注册时，新增项在 `名称列表` 和 `ops 列表` 中的插入位置及绝对索引是否严格一一对应？

**【下一步行动】**
1. **人工确认**：硬件/底层工程师核对旧 ICP 接口兼容性，确认 A2 状态。
2. **代码审查**：重点 Review A3 的数组索引对齐情况，建议引入结构体数组或宏校验机制防呆。
3. **补充设计**：补充 UI/配置层（如设备选择列表、参数配置界面）的适配架构节点。

## 人工审查与补充区

- 审查结论：
- 需要修改的条目：
- 新增条目：
- 删除条目：
- 备注：

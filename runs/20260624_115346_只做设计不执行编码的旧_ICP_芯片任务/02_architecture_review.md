# 架构设计评审：只做设计不执行编码的旧 ICP 芯片任务

| arch_id | linked_requirement | layer_module | design_decision | interface_dependency | user_confirmation | status |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | R1 | 芯片编译宏与名称层 | 在 config_8bit.h 新增 VMODEL_TEST_8BIT 宏和 STR 宏。 | 被 cswrite_cfg_8bit.c 和 UI/配置层引用。 | pending | pending_user_review |
| A2 | R1,R2 | 芯片操作实现层 | 新增 VMODEL_TEST_8BIT.c，按 chip_operation 回调模板实现。 | 依赖 io_icsp.h 的旧 ICP 通信接口。 | pending | pending_user_review |
| A3 | R1,R3 | 注册与调度层 | 在 cswrite_cfg_8bit.c 注册 extern、OPS 宏、名称列表和 ops 列表。 | 名称列表与 ops 列表索引必须一致。 | pending | pending_user_review |

## 大模型阶段判断

- 未启用大模型模式

## 人工审查与补充区

- 审查结论：
- 需要修改的条目：
- 新增条目：
- 删除条目：
- 备注：

# 需求评审：只做设计不执行编码的旧 ICP 芯片任务

| req_id | requirement | source_evidence | acceptance_criteria | user_confirmation | status |
| --- | --- | --- | --- | --- | --- |
| R1 | 新增 8 位旧 ICP 芯片 VMODEL_TEST_8BIT 的软件侧支持。 | 任务输入 + 旧 ICP 芯片参考实现 + 8 位烧录规范 | 芯片宏、名称、ops 注册和芯片实现文件均可被代码引用。 | pending | pending_user_review |
| R2 | 实现时必须复用旧 ICP 通信协议，不误用 SPI 新协议。 | io_icsp 旧 ICP 接口与参考芯片实现 | 新芯片实现文件引用 io_icsp.h，芯片操作回调使用旧 ICP 风格。 | pending | pending_user_review |
| R3 | 测试必须覆盖编码实现、架构设计和需求验收三层。 | 当前工作流规则 | 05_test_cases.md 与 06_test_execution.md 均按三层分组。 | pending | pending_user_review |

## 大模型阶段判断

- 未启用大模型模式

## 人工审查与补充区

- 审查结论：
- 需要修改的条目：
- 新增条目：
- 删除条目：
- 备注：

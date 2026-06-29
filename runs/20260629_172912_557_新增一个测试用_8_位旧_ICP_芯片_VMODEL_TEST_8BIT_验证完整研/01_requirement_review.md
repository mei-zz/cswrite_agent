# 需求评审：新增一个测试用 8 位旧 ICP 芯片 VMODEL_TEST_8BIT，验证完整研发流程

| req_id | requirement | source_evidence | acceptance_criteria | user_confirmation | status |
| --- | --- | --- | --- | --- | --- |
| R1 | 新增 8 位 旧 ICP 芯片 VMODEL_TEST_8BIT 的软件侧支持。 | 任务输入 + 旧 ICP 芯片参考实现 + 8 位烧录规范 + 上下文检索结果 | src/common/config_8bit.h 中存在芯片宏与名称宏，src/middlewave/program/chips/VMODEL_TEST_8BIT.c 存在实现文件，src/common/cswrite_cfg_8bit.c 完成 ops 注册。 | pending | pending_user_review |
| R2 | 实现时必须复用 旧 ICP 通信协议，不误用其他新协议。 | io_icsp 旧 ICP 接口、chip_operation 回调与参考芯片实现 | src/middlewave/program/chips/VMODEL_TEST_8BIT.c 引用 io_icsp.h，read_id/erase/program 回调均走旧 ICP 风格接口。 | pending | pending_user_review |
| R3 | 测试必须覆盖编码实现、架构设计和需求验收三层。 | 当前工作流规则 | 05_test_cases.md 与 06_test_execution.md 均按三层分组。 | pending | pending_user_review |

## 大模型阶段判断

- 未启用大模型模式

## 人工审查与补充区

- 审查结论：
- 需要修改的条目：
- 新增条目：
- 删除条目：
- 备注：

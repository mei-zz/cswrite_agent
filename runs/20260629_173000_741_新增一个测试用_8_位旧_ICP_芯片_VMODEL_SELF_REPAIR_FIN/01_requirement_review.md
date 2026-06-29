# 需求评审：新增一个测试用 8 位旧 ICP 芯片 VMODEL_SELF_REPAIR_FINAL_8BIT，验证 Planner Critic Reflection 自修复流程

| req_id | requirement | source_evidence | acceptance_criteria | user_confirmation | status |
| --- | --- | --- | --- | --- | --- |
| R1 | 新增 8 位 旧 ICP 芯片 VMODEL_SELF_REPAIR_FINAL_8BIT 的软件侧支持。 | 任务输入 + 旧 ICP 芯片参考实现 + 8 位烧录规范 + 上下文检索结果 | src/common/config_8bit.h 中存在芯片宏与名称宏，src/middlewave/program/chips/VMODEL_SELF_REPAIR_FINAL_8BIT.c 存在实现文件，src/common/cswrite_cfg_8bit.c 完成 ops 注册。 | pending | pending_user_review |
| R2 | 实现时必须复用 旧 ICP 通信协议，不误用其他新协议。 | io_icsp 旧 ICP 接口、chip_operation 回调与参考芯片实现 | src/middlewave/program/chips/VMODEL_SELF_REPAIR_FINAL_8BIT.c 引用 io_icsp.h，read_id/erase/program 回调均走旧 ICP 风格接口。 | pending | pending_user_review |
| R3 | 测试必须覆盖编码实现、架构设计和需求验收三层。 | 当前工作流规则 | 05_test_cases.md 与 06_test_execution.md 均按三层分组。 | pending | pending_user_review |

## 大模型阶段判断

**需求重点**
*   **核心目标**：新增 8 位旧 ICP 测试芯片 `VMODEL_SELF_REPAIR_FINAL_8BIT` (ID: 0x12)，用于验证 Planner Critic Reflection 自修复流程。
*   **判断依据**：需参考 `CSU32PX10` 芯片，在 `config_8bit.h`、`cswrite_cfg_8bit.c` 及专属 `.c` 文件中完成宏定义、注册表配置及底层 ops 实现。

**风险点（需人工确认）**
1.  **硬件验证缺失风险**：规格明确真实硬件烧录延后，当前仅依赖 demo 模式。**需确认**：纯软件/模拟验证是否满足自修复流程当前的验收标准。
2.  **参考芯片兼容性风险**：以 `CSU32PX10` 为参考模板。**需确认**：该芯片的旧 ICP 协议实现是否具备自修复流程所需的特定状态机或异常注入机制。
3.  **数据源质量风险**：检索依赖 `examples/fake_docs`。**需确认**：伪造文档中的协议细节是否足以支撑正确的代码生成，避免生成逻辑与真实旧 ICP 协议冲突。

**下一步**
1.  **代码生成**：基于 `CSU32PX10` 模板，生成上述 3 个指定文件的代码。
2.  **流程集成**：将新芯片 ID (`0x12`) 及 ops 接入自修复流程的测试用例中。
3.  **风险闭环**：等待人工确认上述风险点，并制定后续真实硬件接入计划。

## 人工审查与补充区

- 审查结论：
- 需要修改的条目：
- 新增条目：
- 删除条目：
- 备注：

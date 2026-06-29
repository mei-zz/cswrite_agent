# V 模型追溯矩阵：只做设计不执行编码的旧 ICP 芯片任务

## 追溯结论

- 完整性：gap
- 需求数量：3
- 缺口数量：2

## 需求到测试追溯

| requirement_id | architecture_ids | detail_design_ids | code_files | test_cases | execution_result | trace_status |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | A1, A2, A3 | DD1, DD2, DD3 | src/common/config_8bit.h<br>src/common/cswrite_cfg_8bit.c<br>src/middlewave/program/chips/VMODEL_TEST_8BIT.c | TC-ARCH-001, TC-REQ-001 | manual_required | gap |
| R2 | A2 | DD2 | src/middlewave/program/chips/VMODEL_TEST_8BIT.c | TC-DD-002, TC-REQ-001 | fail | gap |
| R3 | A3 | DD3 | src/common/cswrite_cfg_8bit.c | TC-DD-003, TC-REQ-001 | pass | pass |

## 缺口明细

| requirement_id | requirement | architecture_ids | detail_design_ids | test_cases | execution_result | trace_status |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | 新增 8 位 旧 ICP 芯片 VMODEL_TEST_8BIT 的软件侧支持。 | A1, A2, A3 | DD1, DD2, DD3 | TC-ARCH-001, TC-REQ-001 | manual_required | gap |
| R2 | 实现时必须复用 旧 ICP 通信协议，不误用其他新协议。 | A2 | DD2 | TC-DD-002, TC-REQ-001 | fail | gap |
# 详细设计：新增一个测试用 8 位旧 ICP 芯片 VMODEL_TEST_8BIT，验证完整研发流程

| dd_id | linked_arch | file | operation | symbols | verification_point |
| --- | --- | --- | --- | --- | --- |
| DD1 | A1 | src/common/config_8bit.h | 新增 #define VMODEL_TEST_8BIT 0x12，并添加 STR_VMODEL_TEST_8BIT。 | VMODEL_TEST_8BIT, STR_VMODEL_TEST_8BIT | 宏可被 Select-String 检索到。 |
| DD2 | A2 | src/middlewave/program/chips/VMODEL_TEST_8BIT.c | 新增芯片实现，包含 io_icsp.h 和 chip_operation 回调结构体。 | vmodel_test_8bit_ops, chip_operation | 文件存在且包含 io_icsp.h、read_id、program、erase。 |
| DD3 | A3 | src/common/cswrite_cfg_8bit.c | 注册 extern、OPS 宏、芯片名称列表和 ops 列表。 | OPS_VMODEL_TEST_8BIT, cswrite_chip_list, cswrite_chip_ops_list | 名称列表和 ops 列表都包含新芯片。 |

## 大模型阶段判断

- 未启用大模型模式

## 人工审查与补充区

- 审查结论：
- 需要修改的条目：
- 新增条目：
- 删除条目：
- 备注：

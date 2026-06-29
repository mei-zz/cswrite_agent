# 详细设计：新增一个测试用 8 位旧 ICP 芯片 VMODEL_SELF_REPAIR_FINAL_8BIT，验证 Planner Critic Reflection 自修复流程

| dd_id | linked_arch | file | operation | symbols | verification_point |
| --- | --- | --- | --- | --- | --- |
| DD1 | A1 | src/common/config_8bit.h | 新增 #define VMODEL_SELF_REPAIR_FINAL_8BIT 0x12，并添加 STR_VMODEL_SELF_REPAIR_FINAL_8BIT。 | VMODEL_SELF_REPAIR_FINAL_8BIT, STR_VMODEL_SELF_REPAIR_FINAL_8BIT | 宏可被 Select-String 检索到。 |
| DD2 | A2 | src/middlewave/program/chips/VMODEL_SELF_REPAIR_FINAL_8BIT.c | 新增芯片实现，包含 io_icsp.h 和 chip_operation 回调结构体。 | vmodel_self_repair_final_8bit_ops, chip_operation | 文件存在且包含 io_icsp.h、read_id、program、erase。 |
| DD3 | A3 | src/common/cswrite_cfg_8bit.c | 注册 extern、OPS 宏、芯片名称列表和 ops 列表。 | OPS_VMODEL_SELF_REPAIR_FINAL_8BIT, cswrite_chip_list, cswrite_chip_ops_list | 名称列表和 ops 列表都包含新芯片。 |

## 大模型阶段判断

### 判断依据
整体设计已落实到**文件**和**部分宏/变量**，但**函数**和**验证点**颗粒度不足：
1. **文件/宏/变量**：DD1、DD3 已明确具体文件路径、宏名和数组变量名。
2. **函数**：DD2 仅提及回调接口（read_id/program/erase），**未定义具体的 C 函数名及签名**。
3. **验证点**：DD1 仅验证“存在”，DD2/3 缺乏编译和逻辑级验证，颗粒度过粗。

### 遗漏风险
1. **构建系统遗漏（致命）**：DD2 新增 `.c` 文件，但未提及修改 `Makefile` 或 `CMakeLists.txt`，将导致链接失败。
2. **数组索引错位风险**：DD3 中 `cswrite_chip_list`（名称）与 `cswrite_chip_ops_list`（ops）若未严格对齐，会导致烧录器选错芯片或内存越界。
3. **函数命名失控**：DD2 未规定具体函数名（如 `vmodel_..._read_id`），多人协作时易出现命名冲突或不规范。
4. **验证点无效**：DD1 仅用 `Select-String` 查宏存在，无法发现宏值（0x12）写错或字符串宏内容错误的问题。

### 下一步
1. **补充构建设计**：新增 DD4，明确在构建脚本中添加 `VMODEL_SELF_REPAIR_FINAL_8BIT.c`。
2. **细化 DD2 函数定义**：补充具体的函数签名（如 `static int vmodel_self_repair_final_8bit_read_id(...)`）及入参/出参类型。
3. **强化验证点**：
   - DD1：增加验证宏值 `== 0x12` 及字符串内容。
   - DD2：增加“代码可编译通过”及“回调函数指针非空”验证。
   - DD3：增加“名称数组与 ops 数组长度一致且索引严格对齐”的静态检查或单测验证。
4. **明确头文件声明**：在 DD2 或 DD3 中补充 `vmodel_self_repair_final_8bit_ops` 的 `extern` 声明所在的具体 `.h` 文件路径。

## 人工审查与补充区

- 审查结论：
- 需要修改的条目：
- 新增条目：
- 删除条目：
- 备注：

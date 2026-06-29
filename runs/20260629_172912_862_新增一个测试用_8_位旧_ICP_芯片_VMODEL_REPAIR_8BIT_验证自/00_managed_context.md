# 受控上下文：新增一个测试用 8 位旧 ICP 芯片 VMODEL_REPAIR_8BIT，验证自修复流程

## 上下文预算

```json
{
  "max_items_per_source": 6,
  "max_chars_per_item": 900,
  "max_total_chars": 9000,
  "selected_total_chars": 5882
}
```

## 关键约束覆盖

```json
{
  "required_keywords": [
    "VMODEL_REPAIR_8BIT",
    "STR_VMODEL_REPAIR_8BIT",
    "OPS_VMODEL_REPAIR_8BIT",
    "src/common/config_8bit.h",
    "src/common/cswrite_cfg_8bit.c",
    "io_icsp",
    "chip_operation",
    "旧 ICP"
  ],
  "hit_keywords": [
    "VMODEL_REPAIR_8BIT",
    "src/common/config_8bit.h",
    "src/common/cswrite_cfg_8bit.c",
    "io_icsp",
    "chip_operation",
    "旧 ICP"
  ],
  "missed_keywords": [
    "STR_VMODEL_REPAIR_8BIT",
    "OPS_VMODEL_REPAIR_8BIT"
  ],
  "coverage_ratio": 0.75
}
```

## 冲突提示

- 无

## 入选证据索引

| source_type | source | score | char_count |
| --- | --- | --- | --- |
| memories | memories_0 | 3.0 | 900 |
| memories | memories_1 | 3.0 | 900 |
| memories | memories_2 | 3.0 | 900 |
| docs | C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\examples\fake_docs\0011_8位芯片烧录规范.md | 3.0 | 433 |
| code | C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\runs\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\repo\src\middlewave\program\chips\CSU32PX10.c | 3.0 | 619 |
| code | C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\runs\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\repo\src\common\chip_operation.h | 2.0 | 366 |
| code | C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\runs\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\repo\src\common\cswrite_cfg_8bit.c | 2.0 | 706 |
| code | C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\runs\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\repo\src\middlewave\program\chips\io_icsp.h | 2.0 | 353 |
| docs | C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\examples\fake_docs\0003_需求说明书.md | 1.0 | 280 |
| code | C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\runs\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\repo\src\common\config_8bit.h | 1.0 | 425 |

## 入选证据摘要

### Evidence 1: memories / memories_0

{"summary": "一次完整 V 模型研发闭环成功执行。", "chip_spec": {"chip_macro": "VMODEL_TEST_8BIT", "chip_string_macro": "STR_VMODEL_TEST_8BIT", "chip_value": "0x12", "bit_width": 8, "protocol": "old_icp", "protocol_label": "旧 ICP", "symbol_prefix": "vmodel_test_8bit", "ops_symbol": "vmodel_test_8bit_ops", "ops_macro": "OPS_VMODEL_TEST_8BIT", "config_file": "src/common/config_8bit.h", "registry_file": "src/common/cswrite_cfg_8bit.c", "chip_file": "src/middlewave/program/chips/VMODEL_TEST_8BIT.c", "reference_chip": "CSU32PX10", "scope_note": "当前 demo 聚焦旧 ICP 新芯片接入；真实硬件烧录结果通过测试执行阶段标记为后续接入。"}, "artifacts": {"task_analysis": "C:\\Users\\meigang90240\\Desktop\\烧录器agent\\langgraph_cswrite_agent\\runs\\20260629_172912_557_新增一个测试用_8_位旧_ICP_芯片_VMODEL_TEST_8BIT_验证完整研\\00_task_analysis.md", "planner": "C:\\Users\\meigang90240\\Desktop\\烧录器agent\\langgraph_cswrite_agent\\runs\\20260629_172912_557_新增一个测试用_8_位旧_ICP_芯片_

### Evidence 2: memories / memories_1

{"procedure": "相似新增 旧 ICP 芯片任务可复用三步注册模式：src/common/config_8bit.h -> src/middlewave/program/chips/VMODEL_TEST_8BIT.c -> src/common/cswrite_cfg_8bit.c。", "traceability_matrix": {"complete": true, "rows": [{"requirement_id": "R1", "requirement": "新增 8 位 旧 ICP 芯片 VMODEL_TEST_8BIT 的软件侧支持。", "architecture_ids": "A1, A2, A3", "detail_design_ids": "DD1, DD2, DD3", "code_files": "src/common/config_8bit.h<br>src/common/cswrite_cfg_8bit.c<br>src/middlewave/program/chips/VMODEL_TEST_8BIT.c", "test_cases": "TC-ARCH-001, TC-REQ-001", "execution_result": "pass", "trace_status": "pass"}, {"requirement_id": "R2", "requirement": "实现时必须复用 旧 ICP 通信协议，不误用其他新协议。", "architecture_ids": "A2", "detail_design_ids": "DD2", "code_files": "src/middlewave/program/chips/VMODEL_TEST_8BIT.c", "test_cases": "TC-DD-002, TC-REQ-001", "execution_result": "pass", "trace_status": "pass"}, {"requirement_id": "R3", "requirement"

### Evidence 3: memories / memories_2

{"fact": "旧 ICP 新芯片接入需要同时维护宏定义、芯片实现、名称列表和 ops 列表。", "evidence": [{"requirement_id": "R1", "requirement": "新增 8 位 旧 ICP 芯片 VMODEL_TEST_8BIT 的软件侧支持。", "architecture_ids": "A1, A2, A3", "detail_design_ids": "DD1, DD2, DD3", "code_files": "src/common/config_8bit.h<br>src/common/cswrite_cfg_8bit.c<br>src/middlewave/program/chips/VMODEL_TEST_8BIT.c", "test_cases": "TC-ARCH-001, TC-REQ-001", "execution_result": "pass", "trace_status": "pass"}, {"requirement_id": "R2", "requirement": "实现时必须复用 旧 ICP 通信协议，不误用其他新协议。", "architecture_ids": "A2", "detail_design_ids": "DD2", "code_files": "src/middlewave/program/chips/VMODEL_TEST_8BIT.c", "test_cases": "TC-DD-002, TC-REQ-001", "execution_result": "pass", "trace_status": "pass"}, {"requirement_id": "R3", "requirement": "测试必须覆盖编码实现、架构设计和需求验收三层。", "architecture_ids": "A3", "detail_design_ids": "DD3", "code_files": "src/common/cswrite_cfg_8bit.c", "test_ca

### Evidence 4: docs / C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\examples\fake_docs\0011_8位芯片烧录规范.md

{"source": "C:\\Users\\meigang90240\\Desktop\\烧录器agent\\langgraph_cswrite_agent\\examples\\fake_docs\\0011_8位芯片烧录规范.md", "text": "# 0011 8位芯片烧录规范\n\n旧 ICP 芯片需要通过 `io_icsp.h` 暴露的接口完成读 ID、擦除和编程。\n\n新增芯片时需要保持以下软件链路：\n\n1. 在 `config_8bit.h` 添加芯片编译宏和芯片名称 STR 宏。\n2. 在 `src/middlewave/program/chips/<CHIP>.c` 实现 `chip_operation` 回调。\n3. 在 `cswrite_cfg_8bit.c` 注册 extern、OPS 宏、芯片名称列表和 ops 列表。\n4. 芯片名称列表和 ops 列表必须同步维护，避免主机枚举和实际烧录操作错位。\n\n"}

### Evidence 5: code / C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\runs\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\repo\src\middlewave\program\chips\CSU32PX10.c

{"file": "C:\\Users\\meigang90240\\Desktop\\烧录器agent\\langgraph_cswrite_agent\\runs\\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\\repo\\src\\middlewave\\program\\chips\\CSU32PX10.c", "snippet": "#include \"io_icsp.h\"\n#include \"chip_operation.h\"\n\nstatic int csu32px10_read_id(void) { return io_icsp_read_id(); }\nstatic int csu32px10_erase(void) { return io_icsp_chip_erase(); }\nstatic int csu32px10_program(void) { return io_icsp_program(); }\n\nconst struct chip_operation csu32px10_ops = {\n .read_id = csu32px10_read_id,\n .erase = csu32px10_erase,\n .program = csu32px10_program,\n};\n\n"}

### Evidence 6: code / C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\runs\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\repo\src\common\chip_operation.h

{"file": "C:\\Users\\meigang90240\\Desktop\\烧录器agent\\langgraph_cswrite_agent\\runs\\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\\repo\\src\\common\\chip_operation.h", "snippet": "#ifndef CHIP_OPERATION_H\n#define CHIP_OPERATION_H\n\nstruct chip_operation {\n int (*read_id)(void);\n int (*erase)(void);\n int (*program)(void);\n};\n\n#endif\n\n"}

### Evidence 7: code / C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\runs\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\repo\src\common\cswrite_cfg_8bit.c

{"file": "C:\\Users\\meigang90240\\Desktop\\烧录器agent\\langgraph_cswrite_agent\\runs\\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\\repo\\src\\common\\cswrite_cfg_8bit.c", "snippet": "#include \"config_8bit.h\"\n#include \"chip_operation.h\"\n\nextern const struct chip_operation csu32px10_ops;\nextern const struct chip_operation csu38mx10_ops;\n/* EXTERN_END */\n\n#define OPS_CSU32PX10 (&csu32px10_ops)\n#define OPS_CSU38MX10 (&csu38mx10_ops)\n/* OPS_DEFINE_END */\n\nconst char *cswrite_chip_list[] = {\n STR_CSU32PX10,\n STR_CSU38MX10,\n/* CHIP_LIST_END */\n};\n\nconst struct chip_operation *cswrite_chip_ops_list[] = {\n OPS_CSU32PX10,\n OPS_CSU38MX10,\n/* OPS_LIST_END */\n};\n\n"}

### Evidence 8: code / C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\runs\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\repo\src\middlewave\program\chips\io_icsp.h

{"file": "C:\\Users\\meigang90240\\Desktop\\烧录器agent\\langgraph_cswrite_agent\\runs\\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\\repo\\src\\middlewave\\program\\chips\\io_icsp.h", "snippet": "#ifndef IO_ICSP_H\n#define IO_ICSP_H\n\nint io_icsp_read_id(void);\nint io_icsp_chip_erase(void);\nint io_icsp_program(void);\n\n#endif\n\n"}

### Evidence 9: docs / C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\examples\fake_docs\0003_需求说明书.md

{"source": "C:\\Users\\meigang90240\\Desktop\\烧录器agent\\langgraph_cswrite_agent\\examples\\fake_docs\\0003_需求说明书.md", "text": "# 0003 需求说明书\n\n新增 8 位旧 ICP 芯片时，需要复用现有旧 ICP 通信协议，不能误接 SPI 新协议。\n\n验收要求：\n\n- 能在软件侧识别芯片名称。\n- 能通过芯片操作表找到读 ID、擦除、编程三个回调。\n- 测试用例需要覆盖实现细节、架构链路和用户需求验收。\n\n"}

### Evidence 10: code / C:\Users\meigang90240\Desktop\烧录器agent\langgraph_cswrite_agent\runs\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\repo\src\common\config_8bit.h

{"file": "C:\\Users\\meigang90240\\Desktop\\烧录器agent\\langgraph_cswrite_agent\\runs\\20260629_172912_862_新增一个测试用_8_位旧_ICP_芯片_VMODEL_REPAIR_8BIT_验证自\\repo\\src\\common\\config_8bit.h", "snippet": "#ifndef CONFIG_8BIT_H\n#define CONFIG_8BIT_H\n\n#define CSU32PX10 0x10\n#define CSU38MX10 0x11\n/* CHIP_DEFINE_END */\n\n#define STR_CSU32PX10 \"CSU32PX10\"\n#define STR_CSU38MX10 \"CSU38MX10\"\n/* CHIP_STR_END */\n\n#endif\n\n"}

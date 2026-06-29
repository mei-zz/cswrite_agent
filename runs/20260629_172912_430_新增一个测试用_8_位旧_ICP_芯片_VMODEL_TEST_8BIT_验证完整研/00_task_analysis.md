# 任务解析：新增一个测试用 8 位旧 ICP 芯片 VMODEL_TEST_8BIT，验证完整研发流程

## 结构化芯片规格

```json
{
  "chip_macro": "VMODEL_TEST_8BIT",
  "chip_string_macro": "STR_VMODEL_TEST_8BIT",
  "chip_value": "0x12",
  "bit_width": 8,
  "protocol": "old_icp",
  "protocol_label": "旧 ICP",
  "symbol_prefix": "vmodel_test_8bit",
  "ops_symbol": "vmodel_test_8bit_ops",
  "ops_macro": "OPS_VMODEL_TEST_8BIT",
  "config_file": "src/common/config_8bit.h",
  "registry_file": "src/common/cswrite_cfg_8bit.c",
  "chip_file": "src/middlewave/program/chips/VMODEL_TEST_8BIT.c",
  "reference_chip": "CSU32PX10",
  "scope_note": "当前 demo 聚焦旧 ICP 新芯片接入；真实硬件烧录结果通过测试执行阶段标记为后续接入。"
}
```

## Agent 场景

- 自然语言任务结构化
- LLM 风险审查
- 确定性规格驱动后续节点

## 大模型风险补充

- 未启用大模型模式
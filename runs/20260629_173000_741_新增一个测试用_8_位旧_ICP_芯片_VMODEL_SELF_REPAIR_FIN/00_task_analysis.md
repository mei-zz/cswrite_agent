# 任务解析：新增一个测试用 8 位旧 ICP 芯片 VMODEL_SELF_REPAIR_FINAL_8BIT，验证 Planner Critic Reflection 自修复流程

## 结构化芯片规格

```json
{
  "chip_macro": "VMODEL_SELF_REPAIR_FINAL_8BIT",
  "chip_string_macro": "STR_VMODEL_SELF_REPAIR_FINAL_8BIT",
  "chip_value": "0x12",
  "bit_width": 8,
  "protocol": "old_icp",
  "protocol_label": "旧 ICP",
  "symbol_prefix": "vmodel_self_repair_final_8bit",
  "ops_symbol": "vmodel_self_repair_final_8bit_ops",
  "ops_macro": "OPS_VMODEL_SELF_REPAIR_FINAL_8BIT",
  "config_file": "src/common/config_8bit.h",
  "registry_file": "src/common/cswrite_cfg_8bit.c",
  "chip_file": "src/middlewave/program/chips/VMODEL_SELF_REPAIR_FINAL_8BIT.c",
  "reference_chip": "CSU32PX10",
  "scope_note": "当前 demo 聚焦旧 ICP 新芯片接入；真实硬件烧录结果通过测试执行阶段标记为后续接入。"
}
```

## Agent 场景

- 自然语言任务结构化
- LLM 风险审查
- 确定性规格驱动后续节点

## 大模型风险补充

**判断依据**
- **芯片型号**：`VMODEL_SELF_REPAIR_FINAL_8BIT`。依据 `VMODEL` 前缀与任务描述，判定为验证自修复流程的虚拟测试芯片，非真实物理芯片。
- **位宽**：8位。依据 `bit_width: 8` 及配置文件名 `_8bit` 后缀，判定为 8 位机，解析合理。
- **协议**：旧 ICP (`old_icp`)。依据 `protocol` 字段与任务描述，判定采用旧版 ICP 烧录协议，解析合理。

**需要人工确认的风险**
1. **芯片 ID 冲突**：`chip_value` 设为 `0x12`。需确认该 ID 在旧 ICP 协议芯片库中是否已被真实芯片占用，防止烧录时发生芯片识别冲突。
2. **参考芯片属性**：参考芯片指定为 `CSU32PX10`。需人工确认该芯片是否确为 8 位且使用旧 ICP 协议。若属性不匹配，将导致生成的底层时序和配置代码错误。
3. **无硬件 Mock 风险**：`scope_note` 说明真实硬件烧录延后。需确认当前测试框架是否支持纯软件 Mock 验证。若缺乏 Mock 机制，测试执行阶段将因无真实硬件而直接失败。
4. **工程路径规范**：文件路径包含 `src/middlewave/`。需确认该目录层级是否符合当前项目的实际代码规范，避免生成代码后路径失效或无法编译。

**下一步**
1. 核查 `0x12` ID 唯一性及 `CSU32PX10` 的位宽与协议属性。
2. 确认测试框架的 Mock 支持情况，必要时补充虚拟硬件桩代码。
3. 校验工程目录结构规范，确认无误后推进底层配置与烧录算法代码的生成。
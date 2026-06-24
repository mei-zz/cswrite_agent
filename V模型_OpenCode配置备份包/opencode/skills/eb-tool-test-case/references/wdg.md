# Wdg Module Reference

Use this reference only when generating or updating `KX776_MCAL_工具验收_Wdg.md`.

## Implementation Points To Check

- `WdgDevErrorDetect` is `false` in `Wdg.xdm`. If the requirement says the default is TRUE, keep the test expectation from the requirement and record the implementation difference in the final difference summary.
- Time upper bounds in the current `Wdg.xdm` implementation use `0.16777216` for fast values and `10.73741824` for slow values. If the requirement gives different bounds, write the acceptance test according to the requirement and record the implementation difference.
- `Wdg_Cfg.h` generates macros for DET, disable allowed, initial/max timeout, max timers, version API, Dem report, Dem event, and instance ID.
- The current `Wdg_Cfg.h` template does not generate `WDG_SAFETY_ENABLE`. If the requirement expects it, write the test according to the requirement and record the missing implementation.
- `Wdg_PBcfg.c` currently generates fast/slow reload values, not direct fast/slow timeout millisecond values. If the requirement describes direct millisecond generation, write the expected result from the requirement and record the implementation difference.
- For TOM/ATOM GTM generation, check timer type, mode ID offset, channel ID, ticks, and duplicate channel rejection.
- For Core0/Core1/Core2 reload value checks, Core0/Core1 use `McuCL0Frequency / 3`, and Core2 uses `McuCL1Frequency / 3`.

## Typical Wdg Files

- Requirement document: `工具需求/KX776_MCAL_Wdg_工具需求/KX776_MCAL_工具配置项设计_Wdg.md`
- XDM: `Wdg/config/Wdg.xdm`
- Common template macros: `Wdg/generate/template/Wdg.m`
- Header template: `Wdg/generate/template/inc/Wdg_Cfg.h`
- PB source template: `Wdg/generate/template/src/Wdg_PBcfg.c`

## Difference Summary Format

When Wdg requirements differ from the implementation, add a section to the generated Markdown:

```markdown
## 需求实现差异说明

| 序号 | 关联需求 | 配置项/生成项 | 需求要求 | 当前实现 | 测试用例处理 |
| --- | --- | --- | --- | --- | --- |
| 1 | Wdg_Tool_xxxxx | ExampleItem | 按需求填写 | 按实现填写 | 测试步骤和预期结果按需求编写，执行时如失败按差异记录 |
```

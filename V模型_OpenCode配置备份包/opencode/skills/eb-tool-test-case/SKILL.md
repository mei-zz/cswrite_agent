---
name: eb-tool-test-case
description: Generate KX776 AUTOSAR MCAL EB tresos tool test case Markdown documents such as KX776_MCAL_工具验收_Wdg.md. Use when the user asks to create or update KX776 EB tool validation, acceptance, or test case documents from a reference test document, a KX776_MCAL_Module_工具需求 requirement file, and the module's config/template implementation.
---

# KX776 EB Tool Test Cases

## Purpose

Create Chinese Markdown test case documents for KX776 MCAL EB tresos tool validation. The output should follow the existing reference format, usually `测试用例/KX776_MCAL_工具验收_Eth.md`, and should be detailed enough for an engineer to execute in EB tresos Studio.

Default output is Markdown only. Do not create spreadsheet or other derived formats unless the user explicitly asks for them.

## Inputs

Use the module named by the user as `<Module>`, for example `Wdg`.

If the user does not provide `ReferenceModule`, use `Eth` by default. Search for the Eth reference in the repository first, then use the bundled fallback `references/KX776_MCAL_工具验收_Eth.md`. If no Eth reference can be found in either place, stop before generating the document and ask the user which reference document to use.

Prefer these repository paths:

- Reference acceptance document: `测试用例/KX776_MCAL_工具验收_<ReferenceModule>.md`, usually `Eth`.
- Target requirement document: `工具需求/KX776_MCAL_<Module>_工具需求/KX776_MCAL_工具配置项设计_<Module>.md`.
- Alternate requirement document, when the repository copy is missing or stale: `D:\AI\workspace\eb-tool-review\KX776_MCAL_<Module>_工具需求\KX776_MCAL_工具配置项设计_<Module>.md`.
- Target configuration model: `<Module>/config/<Module>.xdm`.
- Target generator templates: `<Module>/generate/template/`.
- Plugin metadata when useful: `<Module>/plugin.xml`.

Use `rg --files` and `rg` first. If a file is missing, search by module name and `工具需求` or `工具验收` before asking the user.

Bundled references:

- `references/KX776_MCAL_工具验收_Eth.md`: fallback Eth reference format.
- `references/wdg.md`: Wdg-specific implementation notes. Read only when `<Module>` is `Wdg`.

## Workflow

1. Read the reference acceptance document and copy its table shape:
   - `序号`
   - `测试标题`
   - `前置条件`
   - `测试步骤`
   - `预期结果`
   - `关联需求`
   - `测试状态`
   - `测试结果`
2. Read the target requirement document by sections:
   - `UI`: default values, data types, ranges, enums, multiplicity, accepted/rejected status, requirement IDs.
   - `校验`: invalid combinations, expected error messages, generator-stage errors.
   - `关联`: dependencies between configuration parameters and referenced modules.
   - `代码生成`: generated macros, structures, members, formulas, output files.
3. Build a traceability inventory before writing any test case:
   - Prefer the curated top-level sections named exactly `## UI`, `## 关联`, `## 校验`, and `## 代码生成`.
   - Treat later exported raw sheets such as `## Sheet4` only as secondary evidence unless no curated section exists.
   - Normalize Markdown escapes in identifiers, for example `ECUC\_Ocu\_00138` is the same as `ECUC_Ocu_00138`.
   - For each `UI` row, capture `配置编号`, `父节点`, `配置项名称`, `配置项状态`, `PB/PC`, `数据类型`, `多样性`, `初始值`, `数据范围`, `代码实现`, `设计描述`, and `备注`.
   - Keep rows whose `配置编号` is `NaN`; they are still requirements when `配置项名称` is present.
   - If duplicate rows disagree, keep the curated top-level section as authoritative and add the conflict to the difference summary.
4. Read the target module implementation:
   - In `config/*.xdm`, confirm defaults, ranges, enum values, editability, multiplicity, reference paths, and XDM validation expressions.
   - In `generate/template/*.m`, identify generator validations, formulas, references to other modules, and exact error text.
   - In `generate/template/inc/*` and `generate/template/src/*`, identify generated file names, macros, structures, arrays, members, comments, and value mapping rules.
5. Reconcile requirement and implementation:
   - Write test steps and expected results according to the requirement.
   - Use implementation reading to identify feasibility, generated file locations, actual validation sites, and exact code paths, but do not silently change expected results to match implementation.
   - When the requirement differs from implementation, keep the requirement-based test expectation and record the difference in the generated document's final difference summary.
   - Use requirement-provided error text when available. If only implementation error text exists, use it as supporting detail and record that it is implementation-derived.
   - If the requirement says a configuration item is `完全接受` or `新增`, do not classify it as rejected only because XDM marks it `EDITABLE=false`; treat that as a requirement/implementation difference.
   - If the requirement says an item is `拒绝`, do not generate acceptance test cases for it. Record it only in the coverage/omission summary when needed, with the reason `需求状态为拒绝，不纳入工具验收测试`.
6. Generate `测试用例/KX776_MCAL_工具验收_<Module>.md`.
7. Run the validation checks in this skill and fix the document before finishing. Do not leave known validation failures in the output and only report success after the checks pass.

## Requirement ID Rules

Do not invent requirement IDs.

- Copy exact IDs from the requirement document, preserving their family, for example `ECUC_Ocu_00138`, `Csx_Ocu_015`, or `Wdg_Tool_00003`.
- If a requirement row has no explicit ID, use `配置项:<配置项名称>` or `代码生成:<生成项名称>` in `关联需求`.
- Do not create synthetic IDs such as `Ocu_Tool_00001` unless that exact token appears in the target requirement document.
- Do not write ID ranges such as `Ocu_Tool_00004~Ocu_Tool_00011` unless the source document itself uses that range. Prefer listing exact IDs or item names.
- When one test covers several rows, list all exact IDs or item names on the first row, separated by `; `.
- Every numbered test case row must have a non-`NaN` `关联需求`. If no formal ID exists, use one of `配置项:<配置项名称>`, `校验:<配置项名称>`, `关联:<配置项名称>`, or `代码生成:<生成项名称>`.
- Continuation rows must keep `关联需求` as `NaN`. If a continuation row needs a different requirement link, split it into a separate numbered test case or move all covered IDs/names to the first row.

## Difference Handling Rules

Requirement/implementation differences must be visible and internally consistent.

- Main test expectations are the acceptance criteria. When a requirement differs from implementation, the main table should keep the requirement-based expectation unless the requirement itself explicitly documents the implementation-specific behavior, such as `部分接受` with a fixed value.
- Do not write conditional expected results such as `如 XDM 校验通过`, `如不报错则记录差异`, `执行时确认实际行为`, or `按实际生成结果记录`. A test row must have one clear expected result.
- If a test intentionally validates the current implementation despite a requirement mismatch, say so in the test title, link the related difference entry, and make the difference summary state that this is an implementation-observation test rather than acceptance criteria.
- Difference summary entries must agree with the main table. Do not say `测试步骤和预期结果按需求编写` if the main table uses the implementation value.
- Do not omit a requirement only because the implementation is missing it. For missing generated items, include a requirement-based test case that expects the item, then record the current implementation gap in `需求实现差异说明`.
- Compare all defaults, ranges, editability, enum lists, multiplicity, status, error text, generated macro names, generated values, and CommonPublishedInformation labels. Any mismatch must either appear in the main test expectation or in `需求实现差异说明`.

## Test Case Design

Cover these categories when applicable:

- UI defaults, type, range, enum options, editability, and multiplicity.
- Accepted, partially accepted, and custom/new configuration items.
- Container existence and hierarchy.
- Reference validity for Mcu, Gtm, Dem, or other modules.
- Cross-parameter constraints from the requirement `关联` section and XDM expressions.
- Generator-stage negative cases from `*.m` macros.
- Code generation checks for headers and source files.
- Formulas and derived values, including unit conversion, reload values, ticks, indexes, IDs, or pointers.
- Requirement/implementation differences that affect acceptance criteria.

Before generating the table, confirm the coverage plan:

- Every non-empty `配置项名称` in the authoritative `UI` inventory is covered by a test case or explicitly listed in the final difference/omission summary. Rows whose status is `拒绝` are normally listed as omitted, not tested.
- `完全接受`, `部分接受`, and `新增` rows are not mixed into a single vague test when their expected behavior differs.
- Boolean API switches may be grouped only when the expected generated macro names are all listed exactly and each switch has the same default, range, and generation rule.
- Code-generation tests use exact macro, structure, array, member, and file names copied from templates or requirement snippets.
- Setup actions must have a meaningful expected result such as `配置保存并校验通过`; do not put `NaN` in `预期结果`.

Use practical EB tresos actions: add modules, configure values, save or validate, run Generate, and inspect generated files.

## Test Step Detail Rules

Write steps so that an engineer can execute them without guessing.

Each `测试步骤` row should include these details when applicable:

- EB tresos location: module, container path, and parameter name, for example `Ocu/OcuConfigSet/OcuChannel/<channel>/OcuChannelId`.
- Concrete input data: exact values, boundary values, enum names, referenced module nodes, and the number of containers to create.
- Trigger action: save, validate, run Generate, or inspect a generated file.
- Inspection target: generated file name plus exact macro, structure, array, member, or error message to check.

Avoid vague steps:

- Do not write only `查看可选项`, `检查对应宏`, `生成代码并检查 Ocu_Cfg.h`, `依次勾选各 API 开关`, or `添加多个实例`.
- Rewrite them with exact objects and data, for example `在 OcuConfigurationOfOptionalApis 中依次设置 OcuDeInitApi=true、OcuGetCounterApi=true ...，保存并执行 Validate`.
- For grouped boolean switches, list every switch and every expected macro name in the expected result, or split into separate cases if the row becomes hard to read.
- For reference tests, describe the referenced module setup, for example `在 Gtm/Atom/Atom_0/AtomChannel_0 设置 AtomChannelUsage=USED_BY_OCU_DRIVER` before selecting it in the target module.
- For negative tests, put one invalid condition per row unless two values share exactly the same expected diagnostic.
- For generated-code tests, include enough expected text to identify the exact output, not just "生成正确".

Every `预期结果` row should be directly observable:

- UI expectation: visible, hidden, editable, non-editable, default value, enum list, range validation result, or exact diagnostic text.
- Generate expectation: file appears, macro expands to exact value, structure member contains exact value, array count/order matches configuration, or MemMap pair exists.
- Setup rows still need expected results, such as `配置保存成功且 Validate 无错误`; never leave setup expectations as `NaN`.

## Module-Specific Guardrails

For `Ocu`, pay attention to these known failure modes:

- The curated Ocu requirement uses `ECUC_Ocu_*` and `Csx_Ocu_*` identifiers, not `Ocu_Tool_*`; do not synthesize `Ocu_Tool_*` IDs.
- `OcuOutputPinDefaultState` has a requirement default of `OCU_HIGH` in the curated UI section, while the current XDM default is `OCU_LOW`; the main acceptance expectation stays requirement-based and the mismatch goes to `需求实现差异说明`.
- `OcuHardwareTriggeredDMA` is marked `完全接受` in the curated UI section but the current XDM marks it non-editable; treat this as a difference, not as a normal rejected-item test.
- Ocu rows whose authoritative status is `拒绝` must not become acceptance test cases. If coverage accounting is needed, list them in the omission/difference summary as `需求状态为拒绝，不纳入工具验收测试`.
- The Ocu requirement examples may show `OCU_CFG_*` version macros, while the current template generates `OCU_*` version macros. Record this as a requirement/implementation difference if both are observed.
- `OcuRuntimeErrorDetect`, `OcuChannelId`, `OcuHwChannelUsed`, and `OcuHwTimerUsed` may have no explicit curated UI ID. Link them as `配置项:<name>` or to exact `Csx_Ocu_*` code-generation IDs when present; never leave the numbered row's `关联需求` as `NaN`.
- `OcuChannelId` has requirement error text `The logic channel number must be unique, and it must be conssective`, while current XDM has separate messages for duplicate and non-consecutive values. Record the message split as a difference if the test uses implementation-specific messages.
- `OcuDefaultThreshold` has requirement validation `<=0xFFFFFF`. Do not add an acceptance row expecting `4294967295` to generate successfully; if current XDM permits it, record that as a difference.
- `OCULIB_INSTANCE_ID` is listed in the Ocu code-generation requirements. Even if the current template does not generate it, include a requirement-based test case and record the implementation gap.
- For Ocu CommonPublishedInformation, compare requirement defaults and XDM defaults for `Ar*`, `Sw*`, `ModuleId`, `VendorId`, and `Release`; do not silently use implementation defaults in the main expectation without a difference entry.

## Table Formatting Rules

Use one row per test step.

For each test case:

- Put integer `序号` only on the first row, for example `1`, `2`, `3`.
- Put `测试标题`, `前置条件`, `关联需求`, `测试状态`, and `测试结果` only on the first row.
- Put `NaN` in those columns on continuation rows.
- Put exactly one action in each `测试步骤` cell.
- Put the expected result for that specific action in the same row's `预期结果` cell.
- Never put `NaN` in `测试步骤` or `预期结果`. Split or rewrite the test if a setup action seems to have no expected result.
- Use `NaN` only when the reference document style requires an intentionally blank continuation metadata cell.
- Keep requirement IDs on the first row of the test case unless the reference document uses a different convention.
- Use Chinese text for titles, steps, and expected results.
- The `## Sheet1` acceptance table must have exactly 8 columns: `序号`, `测试标题`, `前置条件`, `测试步骤`, `预期结果`, `关联需求`, `测试状态`, `测试结果`.
- The `## 需求实现差异说明` table must have exactly 6 columns: `序号`, `关联需求`, `配置项/生成项`, `需求要求`, `当前实现`, `测试用例处理`. Do not add `测试状态`, `测试结果`, or `NaN` columns to this summary table.

Example:

```markdown
| 序号 | 测试标题 | 前置条件 | 测试步骤 | 预期结果 | 关联需求 | 测试状态 | 测试结果 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | WdgIndex 初值、范围和实例 ID 宏生成测试 | 已添加 Wdg 模块 | 1. 打开 `Wdg/WdgGeneral`，查看 `WdgIndex` 初始值 | 初始值为 `0` | Wdg_Tool_00003 | 待执行 | 待填写 |
| NaN | NaN | NaN | 2. 依次配置 `WdgIndex=0`、`WdgIndex=255` 并校验 | `0`、`255` 均校验通过 | NaN | NaN | NaN |
| NaN | NaN | NaN | 3. 依次配置 `WdgIndex=-1`、`WdgIndex=256` 并校验 | 小于 `0` 或大于 `255` 时报范围错误 | NaN | NaN | NaN |
```

## Output Structure

Start with a short title:

```markdown
# KX776_MCAL_工具验收_<Module>
```

Add `执行说明` when the document needs common setup, module dependencies, or generated output locations. Put detailed requirement/implementation differences in the final summary section, not only in `执行说明`.

Then add `## Sheet1` with the acceptance table. Do not add empty `Sheet2` or `Sheet3` unless the reference document or user explicitly requires them.

Do not put requirement rows whose authoritative `配置项状态` is `拒绝` into `Sheet1`. If documenting them is useful for traceability, add a short final section:

```markdown
## 未测试项说明

| 序号 | 配置项 | 关联需求 | 不测试原因 |
| --- | --- | --- | --- |
| 1 | ExampleRejectedItem | ECUC_xxx | 需求状态为拒绝，不纳入工具验收测试 |
```

When requirement and implementation differ, append a final summary section:

```markdown
## 需求实现差异说明

| 序号 | 关联需求 | 配置项/生成项 | 需求要求 | 当前实现 | 测试用例处理 |
| --- | --- | --- | --- | --- | --- |
| 1 | Wdg_Tool_xxxxx | ExampleItem | 按需求填写 | 按实现填写 | 测试步骤和预期结果按需求编写，执行时如失败按差异记录 |
```

## Validation

After editing, run these checks from the repository root.

Check table columns:

```powershell
$bad=@(); $i=0; Get-Content "测试用例\KX776_MCAL_工具验收_<Module>.md" | ForEach-Object { $i++; if($_ -like '|*|'){ $count=($_.ToCharArray() | Where-Object { $_ -eq '|' }).Count; if($count -ne 9){ $bad += "${i}: $count pipes" } } }; if($bad.Count -eq 0){ 'All table rows have 8 columns.' } else { $bad }
```

Check integer test case count:

```powershell
Select-String -Path "测试用例\KX776_MCAL_工具验收_<Module>.md" -Pattern '^\| [0-9]+ \|' | Measure-Object | Select-Object -ExpandProperty Count
```

Check no decimal sequence remains:

```powershell
Select-String -Path "测试用例\KX776_MCAL_工具验收_<Module>.md" -Pattern '^\| [0-9]+\.0 \|' | Measure-Object | Select-Object -ExpandProperty Count
```

Check no step or expected result cell is `NaN`:

```powershell
$bad=@(); $i=0; Get-Content "测试用例\KX776_MCAL_工具验收_<Module>.md" | ForEach-Object { $i++; if($_ -like '|*|'){ $cols=$_ -split '\|'; if($cols.Count -ge 9 -and ($cols[4].Trim() -eq 'NaN' -or $cols[5].Trim() -eq 'NaN')){ $bad += "${i}: $_" } } }; if($bad.Count -eq 0){ 'No NaN in step or expected-result cells.' } else { $bad }
```

Check no numbered test case has `NaN` requirement link:

```powershell
$bad=@(); $i=0; Get-Content "测试用例\KX776_MCAL_工具验收_<Module>.md" | ForEach-Object { $i++; if($_ -match '^\| [0-9]+ \|'){ $cols=$_ -split '\|'; if($cols.Count -ge 9 -and $cols[6].Trim() -eq 'NaN'){ $bad += "${i}: $_" } } }; if($bad.Count -eq 0){ 'All numbered test cases have requirement links.' } else { $bad }
```

Check continuation rows do not carry requirement links:

```powershell
$bad=@(); $i=0; Get-Content "测试用例\KX776_MCAL_工具验收_<Module>.md" | ForEach-Object { $i++; if($_ -match '^\| NaN \|'){ $cols=$_ -split '\|'; if($cols.Count -ge 9 -and $cols[6].Trim() -ne 'NaN'){ $bad += "${i}: $_" } } }; if($bad.Count -eq 0){ 'Continuation requirement cells are NaN.' } else { $bad }
```

Check the difference summary has exactly 6 columns and no `NaN` headers:

```powershell
$lines=Get-Content "测试用例\KX776_MCAL_工具验收_<Module>.md"; $start=($lines | Select-String '^## 需求实现差异说明' | Select-Object -First 1).LineNumber; $bad=@(); if($start){ for($i=$start; $i -le $lines.Count; $i++){ $line=$lines[$i-1]; if($line -like '|*|'){ $pipes=($line.ToCharArray() | Where-Object { $_ -eq '|' }).Count; if($pipes -ne 7 -or $line -match '\| *NaN *\|'){ $bad += "${i}: $pipes pipes: $line" } } } }; if($bad.Count -eq 0){ 'Difference summary has 6 columns.' } else { $bad }
```

Check no conditional expected result remains in `Sheet1`:

```powershell
$bad=@(); $i=0; Get-Content "测试用例\KX776_MCAL_工具验收_<Module>.md" | ForEach-Object { $i++; if($_ -like '|*|' -and $_ -match '如|如果|若实际|执行时确认|记录差异|按实际'){ $bad += "${i}: $_" } }; if($bad.Count -eq 0){ 'No conditional expected-result wording detected.' } else { $bad }
```

Check no rejected requirement item is tested in `Sheet1`:

```powershell
$doc=Get-Content "测试用例\KX776_MCAL_工具验收_<Module>.md" -Raw; $req=Get-Content "工具需求\KX776_MCAL_<Module>_工具需求\KX776_MCAL_工具配置项设计_<Module>.md"; $rejected=@(); foreach($line in $req){ if($line -match '\|[^|]*\|[^|]*\|[^|]*\|([^|]+)\|\s*拒绝\s*\|'){ $name=$Matches[1].Trim(); if($name -and $name -ne '配置项名称'){ $rejected += [regex]::Escape($name) } } }; $hits=@(); foreach($name in ($rejected | Sort-Object -Unique)){ if($doc -match "^\| [0-9]+ \|[^`r`n]*$name"){ $hits += $name } }; if($hits.Count -eq 0){ 'No rejected items are tested in Sheet1.' } else { $hits }
```

Check synthetic Tool IDs were not introduced:

```powershell
$reqText=Get-Content "工具需求\KX776_MCAL_<Module>_工具需求\KX776_MCAL_工具配置项设计_<Module>.md" -Raw; $ids=Select-String -Path "测试用例\KX776_MCAL_工具验收_<Module>.md" -Pattern '<Module>_Tool_[0-9]+' -AllMatches | ForEach-Object { $_.Matches.Value } | Sort-Object -Unique; $missing=$ids | Where-Object { $reqText -notmatch [regex]::Escape($_) }; if($missing.Count -eq 0){ 'No synthetic <Module>_Tool IDs detected.' } else { $missing }
```

Manually verify the coverage inventory:

- All authoritative `UI` rows with a real `配置项名称` are either covered or listed as omitted with a reason.
- Rows whose authoritative status is `拒绝` are not present as numbered test cases; if mentioned, they are only listed in an omission/difference summary with a clear no-test reason.
- Difference summary entries exist for every default, range, editability, status, macro-name, or generated-code mismatch discovered during implementation reading.

Read the first lines of the document and spot-check a middle and final test case to confirm that steps and expected results remain aligned.

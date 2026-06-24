# 测试用例：新增一个测试用 8 位旧 ICP 芯片 VMODEL_TEST_8BIT，验证完整研发流程

- Skill：已读取 Skill：C:\Users\meigang90240\.config\opencode\skills\eb-tool-test-case\SKILL.md，长度 20551 字符

## 1. 详细设计/编码验证用例

| case_id | verify_level | target | case_type | steps | expected |
| --- | --- | --- | --- | --- | --- |
| TC-DD-001 | detail_design_verification | DD1 | static | 检查 config_8bit.h 是否存在 VMODEL_TEST_8BIT 和 STR 宏。 | 两个宏均存在且命名一致。 |
| TC-DD-002 | detail_design_verification | DD2 | static | 检查 VMODEL_TEST_8BIT.c 是否包含 io_icsp.h 和 chip_operation。 | 使用旧 ICP 接口并导出 vmodel_test_8bit_ops。 |

## 2. 架构设计验证用例

| case_id | verify_level | target | case_type | steps | expected |
| --- | --- | --- | --- | --- | --- |
| TC-ARCH-001 | architecture_verification | A1+A2+A3 | integration | 检查编译宏、芯片实现、注册表三层是否形成完整链路。 | 名称列表和 ops 列表均包含新芯片，索引关系可维护。 |

## 3. 需求验收用例

| case_id | verify_level | target | case_type | steps | expected |
| --- | --- | --- | --- | --- | --- |
| TC-REQ-001 | requirement_acceptance | R1+R2+R3 | acceptance | 基于需求清单回溯验证旧 ICP 新芯片支持、协议选择和三层测试覆盖。 | 所有已确认需求均有设计、代码和测试证据。 |

## 4. 边界值、反例和错误处理用例

- TC-NEG-001：名称列表存在但 ops 列表缺失时，应判定注册不完整。
- TC-BOUND-001：芯片宏值冲突时，应阻断合入并提示重新分配。

## 5. 静态检查 / dry-run 命令

```powershell
Select-String -Path src/common/config_8bit.h -Pattern VMODEL_TEST_8BIT
Select-String -Path src/common/cswrite_cfg_8bit.c -Pattern OPS_VMODEL_TEST_8BIT
Select-String -Path src/middlewave/program/chips/VMODEL_TEST_8BIT.c -Pattern io_icsp.h
```

## 大模型阶段判断

- 未启用大模型模式

## 人工审查与补充区

- 审查结论：
- 需要修改的条目：
- 新增条目：
- 删除条目：
- 备注：

## 执行记录区

- 待执行
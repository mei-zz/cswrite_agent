# Critic 一致性审查：只做设计不执行编码的旧 ICP 芯片任务

## 结论

- 状态：fail
- 问题数：9
- 可自动修复：False
- 建议回退节点：无

## 问题明细

| issue_id | severity | category | evidence | repair_target |
| --- | --- | --- | --- | --- |
| CRIT-TEST-001 | high | test_failure | src/common/config_8bit.h 未包含 VMODEL_TEST_8BIT | coding |
| CRIT-TEST-002 | high | test_failure | src/common/config_8bit.h 未包含 STR_VMODEL_TEST_8BIT | coding |
| CRIT-TEST-003 | high | test_failure | src/middlewave/program/chips/VMODEL_TEST_8BIT.c 不存在 | coding |
| CRIT-TEST-004 | high | test_failure | src/middlewave/program/chips/VMODEL_TEST_8BIT.c 不存在 | coding |
| CRIT-TEST-005 | high | test_failure | src/common/cswrite_cfg_8bit.c 未包含 OPS_VMODEL_TEST_8BIT | coding |
| CRIT-TEST-006 | high | test_failure | src/common/cswrite_cfg_8bit.c 未包含 STR_VMODEL_TEST_8BIT | coding |
| CRIT-TEST-007 | high | test_failure | 至少一个详细设计检查失败 | coding |
| CRIT-TEST-008 | high | test_failure | demo 静态检查证明软件链路完整；真实烧录需后续接入专用测试环境。 | coding |
| CRIT-TEST-009 | high | test_failure | src/middlewave/program/chips/VMODEL_TEST_8BIT.c 不存在 | coding |

## 大模型阶段判断

- 未启用大模型模式
## Sheet1
| 序号 | 测试标题 | 前置条件 | 测试步骤 | 预期结果 | 关联需求 | 测试状态 | 测试结果 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1.0 | EthTimeoutDuration初值/范围测试 | NaN | 1.配置EthTimeoutDuration为32768 | 初始值为5000 | Eth\_Tool\_001 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthTimeoutDuration为0 | 小于1时报错 | NaN | NaN | NaN |
| NaN | NaN | NaN | 3.配置EthTimeoutDuration为65536 | 大于65535时报错 | NaN | NaN | NaN |
| 2.0 | EthCrcStriping初值/编辑测试 | NaN | 1.查看默认值和是否可编辑 | 默认值为TRUE且不可编辑 | Eth\_Tool\_002 | NaN | NaN |
| 3.0 | EthMaxCtrlsSupported初值/编辑测试 | NaN | 1.查看是否有默认值 | 默认值为1 | Eth\_Tool\_003 | NaN | NaN |
| NaN | NaN | NaN | 2.验证是否可编辑 | 配置项不可编辑 | NaN | NaN | NaN |
| 4.0 | EthIndex初值/编辑测试 | NaN | 1.查看默认值和是否可编辑 | 默认值为0且不可编辑 | Eth\_Tool\_004 | NaN | NaN |
| 5.0 | EthDuplexMode初值/枚举范围测试 | NaN | 1.查看可选择的选项和初始值 | 可选ETH\_HALF\_DUPLEX,ETH\_FULL\_DUPLEX\n初值为ETH\_FULL\_DUPLEX | Eth\_Tool\_005 | NaN | NaN |
| NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 6.0 | EthCtrlMacLayerType\n初值/枚举范围测试 | NaN | 1.查看枚举范围 | 可选ETH\_MAC\_LAYER\_TYPE\_XGMII, \nETH\_MAC\_LAYER\_TYPE\_XMII\n初值为ETH\_MAC\_LAYER\_TYPE\_XMII | Eth\_Tool\_006 | NaN | NaN |
| NaN | NaN | NaN | 2.不能配置为XXGMII | NaN | NaN | NaN | NaN |
| 7.0 | EthRxBufLenByte初值/范围测试 | NaN | 1.查看配置项的初始值 | 初始值为256 | Eth\_Tool\_011 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthRxBufLenByte<0和>1524 | 超出范围[0,1524]时报错 | NaN | NaN | NaN |
| 8.0 | EthTxBufLenByte初值/范围测试 | NaN | 1.查看配置项的初始值 | 初始值为256 | Eth\_Tool\_012 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthTxBufLenByte<0和>1524 | 超出范围[0,1524]时报错 | NaN | NaN | NaN |
| 9.0 | EthRxBuffTotal初值/范围测试 | NaN | 1.查看配置项的初始值 | 初始值为4 | Eth\_Tool\_013 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthRxBuffTotal<0和>255 | 超出范围[0,255]时报错 | NaN | NaN | NaN |
| 10.0 | EthTxBuffTotal初值/范围测试 | NaN | 1.查看配置项的初始值 | 初始值为4 | Eth\_Tool\_014 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthTxBuffTotal<0和>255 | 超出范围[0,255]时报错 | NaN | NaN | NaN |
| 11.0 | EthTxQueueSize初值/范围测试 | NaN | 1.查看配置项的初始值 | 初始值为7 | Eth\_Tool\_015 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthTxQueueSize<0和>15 | 超出范围[0,15]时报错 | NaN | NaN | NaN |
| 12.0 | EthRxQueueSize初值/范围测试 | NaN | 1.查看配置项的初始值 | 初始值为7 | Eth\_Tool\_016 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthRxQueueSize<0和>31 | 超出范围[0,31]时报错 | NaN | NaN | NaN |
| 13.0 | EthMdioAlternateInput\n初值/枚举范围测试 | NaN | 1.查看初始值 | 初始值为ALT2\_SELECT\_P12\_1 | Eth\_Tool\_017 | NaN | NaN |
| NaN | NaN | NaN | 2.查看可选项 | 可选ALT0\_SELECT\_P00\_0,\nALT2\_SELECT\_P12\_1, \nALT3\_SELECT\_P21\_3 | NaN | NaN | NaN |
| NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 14.0 | EthRxclkAlternateInput初值/枚举范围\n及约束范围测试\nMII和RGMII模式下可配置\nRGMII模式下只可选ALT0 | NaN | 1.查看初始值 | 初始值为ALT0\_SELECT\_P11\_12 | Eth\_Tool\_018 | NaN | NaN |
| NaN | NaN | NaN | 2.查看可选项 | 可选值为ALT0\_SELECT\_P11\_12, \nALT1\_SELECT\_P11\_4, \nALT2\_SELECT\_P12\_0 | NaN | NaN | NaN |
| NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 3.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XMII   配置EthCtrlMacLayerSubType为STANDARD | EthRxclkAlternateInput可配置 | NaN | NaN | NaN |
| NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 4.配置EthCtrlMacLayerType=ETH\_MAC\_LAYER\_TYPE\_XGMII配置EthCtrlMacLayerSubType为REDUCED,选择不同的Pin脚 | 配置除ALT0以外的引脚均报错 | NaN | NaN | NaN |
| NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 15.0 | EthRefclkAlternateInput\n初值/枚举范围测试\nRMII模式下可配置 | NaN | 1.查看初始值和枚举选项 | 仅可选ALT0\_SELECT\_P11\_12且为初值 | Eth\_Tool\_019 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XMII\n配置EthCtrlMacLayerSubType为REDUCED | 此时EthRefclkAlternateInput可修改 | NaN | NaN | NaN |
| NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 16.0 | EthCrsAlternateInput\n初值/枚举范围测试\nMII模式下可配置 | NaN | 1.查看初始值和枚举选项 | 初值为ALT0\_SELECT\_P11\_14\n可选ALT0\_SELECT\_P11\_14, ALT1\_SELECT\_P11\_11 | Eth\_Tool\_020 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XMII\n配置EthCtrlMacLayerSubType为STANDARD | 此时EthCrsAlternateInput可修改 | NaN | NaN | NaN |
| NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 17.0 | EthColAlternateInput\n初值/枚举范围测试\nMII模式下可配置 | NaN | 1.查看初始值和枚举选项 | 仅可选ALT0\_SELECT\_P11\_15且为初值 | Eth\_Tool\_021 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XMII\n配置EthCtrlMacLayerSubType为STANDARD | 此时EthColAlternateInput可修改 | NaN | NaN | NaN |
| NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 18.0 | EthRxDvAlternateInput\n初值/枚举范围测试\nMII模式下可配置 | NaN | 1.查看初始值和枚举选项 | 初值为ALT0\_SELECT\_P11\_11\n可选ALT0\_SELECT\_P11\_11, ALT1\_SELECT\_P11\_14 | Eth\_Tool\_022 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XMII\n配置EthCtrlMacLayerSubType为STANDARD | 此时EthRxDvAlternateInput可修改 | NaN | NaN | NaN |
| NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 19.0 | EthCrsDvAlternateInput\n初值/枚举范围测试\nRMII模式下可配置 | NaN | 1.查看初始值和枚举选项 | 初值为ALT1\_SELECT\_P11\_14\n可选ALT0\_SELECT\_P11\_11, ALT1\_SELECT\_P11\_14 | Eth\_Tool\_023\nEth\_Tool\_041 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XMII\n配置EthCtrlMacLayerSubType为REDUCED | 此时EthCrsDvAlternateInput可修改 | NaN | NaN | NaN |
| NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 20.0 | EthRctlAlternateInput初值/范围测试 | NaN | 1.查看初始值和枚举选项 | 仅可选ALT0\_SELECT\_P11\_11且为初值 | Eth\_Tool\_024 | NaN | NaN |
| 21.0 | EthRxErAlternateInput\n初值/枚举范围测试\nMII模式下可配置 | NaN | 1.查看初始值和枚举选项 | 初值为ALT0\_SELECT\_P11\_13\n可选ALT0\_SELECT\_P11\_13, ALT1\_SELECT\_P21\_7, ALT2\_SELECT\_P10\_0 | Eth\_Tool\_025 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XMII\n配置EthCtrlMacLayerSubType为STANDARD | 此时EthRxErAlternateInput可修改 | NaN | NaN | NaN |
| NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 22.0 | EthRxd0AlternateInput\n初值/范围测试 | NaN | 1.查看初始值和枚举选项 | 仅可选ALT0\_SELECT\_P11\_10且为初值 | Eth\_Tool\_026 | NaN | NaN |
| 23.0 | EthRxd1AlternateInput\n初值/范围测试 | NaN | 1.查看初始值和枚举选项 | 仅可选ALT0\_SELECT\_P11\_9且为初值 | Eth\_Tool\_027 | NaN | NaN |
| 24.0 | EthRxd2AlternateInput\n初值/范围测试 | NaN | 1.查看初始值和枚举选项 | 仅可选ALT0\_SELECT\_P11\_8且为初值 | Eth\_Tool\_028 | NaN | NaN |
| 25.0 | EthRxd3AlternateInput\n初值/范围测试 | NaN | 1.查看初始值和枚举选项 | 仅可选ALT0\_SELECT\_P11\_7且为初值 | Eth\_Tool\_029 | NaN | NaN |
| 26.0 | EthTxclkAlternateInput\n初值/枚举范围测试\nMII模式下可配置 | NaN | 1.查看初始值和枚举选项 | 初值为ALT0\_SELECT\_P11\_5\n可选ALT0\_SELECT\_P11\_5, ALT1\_SELECT\_P11\_12 | Eth\_Tool\_030 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XMII\n配置EthCtrlMacLayerSubType为STANDARD | 此时EthTxclkAlternateInput可修改 | NaN | NaN | NaN |
| NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 27.0 | EthMDCClockFrequency\n初值范围测试 | NaN | 1.查看初始值和数值范围 | 初始值为2500000\n数值范围为[2500000, 25000000] | Eth\_Tool\_031 | NaN | NaN |
| 28.0 | EthCtrlMacLayerType、\nEthCtrlMacLayerSubType\nEthCtrlMacLayerSpeed关联关系测试 | 需满足需求Eth\_Tool\_048和\nEth\_Tool\_049的限制 | 1.配置EthCtrlMacLayerSpeed为ETH\_MAC\_LAYER\_SPEED\_10M或ETH\_MAC\_LAYER\_SPEED\_100M\n\n | 此时可配置MII、RGMII、RMII均不报错 | Eth\_Tool\_032\nEth\_Tool\_034\n | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerSpeed为ETH\_MAC\_LAYER\_SPEED\_1G | 此时仅可配置为RGMII,其余报错 | NaN | NaN | NaN |
| NaN | NaN | NaN | 3.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XGMII | 此时EthCtrlMacLayerSubType仅可选\nREDUCED,其余报错 | NaN | NaN | NaN |
| NaN | NaN | NaN | 4.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XMII | EthCtrlMacLayerSubType只有\nSTANDARD,REDUCED可选\n其余报错 | NaN | NaN | NaN |
| 29.0 | EthCtrlMacLayerSpeed受EthCtrlIdx\n的约束测试 | NaN | 1.配置EthCtrlIdx指向GETH | EthCtrlMacLayerSpeed可选10M,100M,1G | Eth\_Tool\_033 | NaN | NaN |
| 30.0 | EthRxclkAlternateInput\n在RMII模式下不可配置 | NaN | 1.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XMII\n配置EthCtrlMacLayerSubType为REDUCED | EthRxclkAlternateInput此时不可配置 | Eth\_Tool\_035 | NaN | NaN |
| 31.0 | EthRefclkAlternateInput\n在MII和RGMII下均不可配置 | NaN | 1.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XMII\n配置EthCtrlMacLayerSubType为STANDARD | EthRefclkAlternateInput不可配置 | Eth\_Tool\_036 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XGMII\n配置EthCtrlMacLayerSubType为REDUCED | EthRefclkAlternateInput不可配置 | NaN | NaN | NaN |
| 32.0 | EthRxclkAlternateInput\n在RGMII模式下仅可选\nALT0\_SELECT\_P11\_12 | NaN | 1.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XGMII\n配置EthCtrlMacLayerSubType为REDUCED | EthRxclkAlternateInput仅可选\nALT0\_SELECT\_P11\_12\n其余报错 | Eth\_Tool\_037 | NaN | NaN |
| 33.0 | EthCrsAlternateInput、\nEthColAlternateInput、\nEthRxDvAlternateInput在EthCtrlMacLayerSubType为REDUCED时不可配置\n | NaN | 1.配置EthCtrlMacLayerSubType=REDUCED | EthCrsAlternateInput、\nEthColAlternateInput、\nEthRxDvAlternateInput均不可配置 | Eth\_Tool\_038\nEth\_Tool\_039\nEth\_Tool\_040 | NaN | NaN |
| 34.0 | EthRctlAlternateInput\nRGMII模式下才可配置 | NaN | 1.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XGMII\n配置EthCtrlMacLayerSubType为REDUCED | 仅此情况下可配置,\n其余情况均不可配置 | Eth\_Tool\_042 | NaN | NaN |
| 35.0 | EthRxd2AlternateInput、\nEthRxd3AlternateInput在RMII模式下\n不可配置 | NaN | 1.配置EthCtrlMacLayerType为ETH\_MAC\_LAYER\_TYPE\_XMII\n配置EthCtrlMacLayerSubType为REDUCED | EthRxd2AlternateInput、\nEthRxd2AlternateInput均不可配置 | Eth\_Tool\_043\nEth\_Tool\_044 | NaN | NaN |
| 36.0 | EthTxclkAlternateInput\n当EthCtrlMacLayerSubType为REDUCED时不可配置 | NaN | 1.配置EthCtrlMacLayerSubType=REDUCED | EthTxclkAlternateInput不可配置 | Eth\_Tool\_045 | NaN | NaN |
| 37.0 | MII模式下，\nEthRxDvAlternateInput与EthCrsAlternateInput不能选同一个Pin脚； | NaN | 1.配置EthCtrlMacLayerType=ETH\_MAC\_LAYER\_TYPE\_XMII | 报错"Same hardware pin is selected for \nboth EthRxDvAlternateInput \nand EthCrsAlternateInput." | Eth\_Tool\_046 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerSubType为STANDARD | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 3.配置EthRxDvAlternateInput=ALT0\_SELECT\_P11\_11 | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 4.配置EthCrsAlternateInput=ALT1\_SELECT\_P11\_11 | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 5.修改配置EthRxDvAlternateInput=ALT1\_SELECT\_P11\_14 | 报错消失 | NaN | NaN | NaN |
| NaN | NaN | NaN | 6.修改配置EthCrsAlternateInput=AL0\_SELECT\_P11\_14 | 报错重新出现 | NaN | NaN | NaN |
| 38.0 | MII模式下，\nEthRxclkAlternateInput与EthTxclkAlternateInput不能选同一个Pin脚； | NaN | 1.配置EthCtrlMacLayerType=ETH\_MAC\_LAYER\_TYPE\_XMII | 报错"Same hardware pin is selected for both\nEthRxclkAlternateInput and EthTxclkAlternateInput." | Eth\_Tool\_047 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerSubType为STANDARD | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 3.配置EthRxclkAlternateInput=ALT0\_SELECT\_P11\_12 | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 4.配置EthTxclkAlternateInput=ALT1\_SELECT\_P11\_12 | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 5.修改配置EthRxclkAlternateInput=ALT1\_SELECT\_P11\_4 | 报错消失 | NaN | NaN | NaN |
| NaN | NaN | NaN | 6.修改配置EthTxclkAlternateInput=ALT0\_SELECT\_P11\_5 | 报错未出现 | NaN | NaN | NaN |
| 39.0 | EthCtrlMacLayerSubType不能配置为\nSERIAL\REVERSED | NaN | 1.配置EthCtrlMacLayerSubType=SERIAL | 均报错"EthCtrlMacLayerSubType \ncan't be SERIAL\REVERSED." | Eth\_Tool\_048 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerSubType=REVERSED | NaN | NaN | NaN | NaN |
| 40.0 | EthCtrlMacLayerSpeed不能配置为\nETH\_MAC\_LAYER\_SPEED\_2500M、\nETH\_MAC\_LAYER\_SPEED\_10G | NaN | 1.配置EthCtrlMacLayerSpeed为\nETH\_MAC\_LAYER\_SPEED\_2500M | 报错"EthCtrlMacLayerSpeed can not be configured as \nETH\_MAC\_LAYER\_SPEED\_2500M and ETH\_MAC\_LAYER\_SPEED\_10G." | Eth\_Tool\_049 | NaN | NaN |
| NaN | NaN | NaN | 2.配置EthCtrlMacLayerSpeed为\nETH\_MAC\_LAYER\_SPEED\_10G | 报错"EthCtrlMacLayerSpeed can not be configured as \nETH\_MAC\_LAYER\_SPEED\_2500M and ETH\_MAC\_LAYER\_SPEED\_10G." | NaN | NaN | NaN |
| 41.0 | ethGpctVal值的计算\nMII模式 | NaN | 1.配置EthCtrlMacLayerType=ETH\_MAC\_LAYER\_TYPE\_XMII | 期望值为:\nethGpctlVal = 0x1 << 22 | 0x0 << 20 | 0x0 << 18 | 0x0 << 16 | 0x0 << 14 | 0x0 << 12 | 0x0 << 10 | 0x0 << 8 | 0x0 << 6 | 0x0 << 4 | 0x0 << 2 | 0x0=0x00000000U | Eth\_Tool\_050 | NaN | NaN |
| NaN | NaN | NaN | 2.配置 EthCtrlMacLayerSubType = STANDARD | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 3.配置以下 AlternateInput 参数：\nEthTxclkAlternateInput = ALT0\nEthRxd3AlternateInput = ALT0\nEthRxd2AlternateInput = ALT0\nEthRxd1AlternateInput = ALT0\nEthRxd0AlternateInput = ALT0\nEthRxErAlternateInput = ALT0\nEthRxDvAlternateInput = ALT0\nEthColAlternateInput = ALT0\nEthCrsAlternateInput = ALT0\nEthRxclkAlternateInput = ALT0\nEthMdioAlternateInput = ALT0 | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 4.生成代码并检查生成的Eth\_PBCfg.c文件中的\nethGpctlVal值 | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 5.修改EthMdioAlternateInput=ALT3 | 期望值为:0x00000003U | NaN | NaN | NaN |
| NaN | ethGpctVal值的计算\nRMII模式 | NaN | 1.配置EthCtrlMacLayerType=ETH\_MAC\_LAYER\_TYPE\_XMII | 期望值为\nethGpctlVal = 0x1 << 24 | 0x0 << 20 | 0x0 << 18 | 0x0 << 16 | 0x0 << 14 | 0x0 << 12 | 0x0 << 10 | 0x0 << 8 | 0x0 << 6 | 0x0 << 4 | 0x0 << 2 | 0x0=0x01000000U | NaN | NaN | NaN |
| NaN | NaN | NaN | 2.配置 EthCtrlMacLayerSubType = REDUCED | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 3.配置以下 AlternateInput 参数：\nEthRxd1AlternateInput = ALT0\nEthRxd0AlternateInput = ALT0\nEthCrsDvAlternateInput = ALT0\nEthRefclkAlternateInput = ALT0\nEthMdioAlternateInput = ALT0 | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 4.生成代码并检查生成的Eth\_PBCfg.c文件中的\nethGpctlVal值 | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 5.修改EthCrsDvAlternateInput=ALT1 | 期望值为0x01000100U | NaN | NaN | NaN |
| NaN | ethGpctVal值的计算\nRGMII模式 | NaN | 1.配置EthCtrlMacLayerType=ETH\_MAC\_LAYER\_TYPE\_XGMII | ethGpctlVal = 0x1 << 22 | 0x0 << 20 | 0x0 << 18 | 0x0 << 16 | 0x0 << 14 | 0x0 << 12 | 0x0 << 10 | 0x0 << 8 | 0x0 << 6 | 0x0 << 4 | 0x0 << 2 | 0x0\n期望值：0x00400000U | NaN | NaN | NaN |
| NaN | NaN | NaN | 2.配置 EthCtrlMacLayerSubType = REDUCED | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 3.配置以下 AlternateInput 参数：\nEthRxd3AlternateInput = ALT0\nEthRxd2AlternateInput = ALT0\nEthRxd1AlternateInput = ALT0\nEthRxd0AlternateInput = ALT0\nEthRctlAlternateInput = ALT0\nEthRxclkAlternateInput = ALT0\nEthMdioAlternateInput = ALT0 | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 4.生成代码并检查生成的Eth\_PBCfg.c文件中的\nethGpctlVal值 | NaN | NaN | NaN | NaN |
| NaN | NaN | NaN | 5.修改EthMdioAlternateInput=ALT2 | 期望值0x00400002U | NaN | NaN | NaN |

## Sheet2
|
|  |

## Sheet3
|
|  |
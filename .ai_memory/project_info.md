# 量化策略回测项目关键信息

## 项目概述
- 项目名称: 对冲网格策略量化回测系统
- 创建时间: 2025-08-02 22:46:57
- 主要功能: ETH/USDT对冲网格策略回测与可视化

## 核心文件
- `backtest_kline_trajectory.py`: 主策略引擎，包含ATR风控逻辑
- `后端回测服务器.py`: FastAPI后端服务
- `前端服务器.py`: 简单HTML前端界面
- `test_corrected_atr_logic.py`: 最新的ATR逻辑测试文件

## 技术架构决策
- 后端: Python + FastAPI
- 前端: 计划重构为React + TypeScript
- 数据存储: HDF5 + Pickle缓存
- 风控: ATR波动率自适应机制

## 关键配置
- ATR周期: 24小时
- 高波动阈值: 30%
- 极端波动阈值: 50%
- 紧急平仓阈值: 70%

## 已删除的重复文件
- test_2020_atr_protection.py (已备份)
- test_2020_simple.py (已备份)
- test_improved_atr.py (已备份)
- ATR_CONFIG_说明文档.md (已合并)
- ATR_简化配置说明.md (已合并)

## 下一步计划
1. 完善ATR计算逻辑
2. 实现价格最劣优先平仓
3. React前端重构
4. 数据迁移方案设计

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试回测类型错误
"""

import sys
import traceback
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # 导入回测模块
    from backtest_kline_trajectory import BACKTEST_CONFIG, STRATEGY_CONFIG, run_backtest_with_params
    
    print("✅ 成功导入回测模块")
    
    # 设置测试参数
    BACKTEST_CONFIG.update({
        'start_date': '2025-05-15',
        'end_date': '2025-06-15',
        'initial_balance': 10000.0,  # 确保是float
        'plot_equity_curve': False,
    })
    
    STRATEGY_CONFIG.update({
        'leverage': 5,
        'bid_spread': 0.002,
        'ask_spread': 0.002,
        'max_position_value_ratio': 0.8,
        'position_size_ratio': 0.02
    })
    
    print("✅ 参数设置完成")
    print(f"initial_balance类型: {type(BACKTEST_CONFIG['initial_balance'])}")
    print(f"initial_balance值: {BACKTEST_CONFIG['initial_balance']}")
    
    # 尝试运行回测
    print("🚀 开始运行回测...")
    result = run_backtest_with_params(use_cache=True)
    print("✅ 回测完成")
    print(result)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    print("详细错误信息:")
    traceback.print_exc()

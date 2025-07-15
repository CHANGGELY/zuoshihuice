#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度回测执行器 - 支持实时进度输出的回测执行器
"""

import sys
import json
import argparse
import os
import time
import threading
from pathlib import Path

class ProgressReporter:
    """进度报告器"""
    def __init__(self):
        self.current_progress = 0
        self.total_progress = 100
        self.status = "初始化中..."
        self.start_time = time.time()
        self.running = True
        
    def update(self, current, total, status=""):
        """更新进度"""
        self.current_progress = current
        self.total_progress = total
        if status:
            self.status = status
        
        # 输出进度信息到stderr，这样不会干扰最终的JSON结果
        elapsed = time.time() - self.start_time
        if total > 0:
            percentage = (current / total) * 100
            eta = (elapsed / current * (total - current)) if current > 0 else 0
            print(f"PROGRESS:{current}/{total}:{percentage:.1f}%:{status}:ETA:{eta:.0f}s", 
                  file=sys.stderr, flush=True)
        else:
            print(f"PROGRESS:0/100:0%:{status}:ETA:0s", file=sys.stderr, flush=True)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='进度回测执行器')
    parser.add_argument('--params-file', required=True, help='参数文件路径')
    args = parser.parse_args()

    # 创建进度报告器
    progress = ProgressReporter()
    
    try:
        progress.update(0, 100, "读取参数...")
        
        # 读取参数
        with open(args.params_file, 'r', encoding='utf-8') as f:
            params = json.load(f)

        progress.update(10, 100, "导入回测引擎...")
        
        # 导入回测引擎
        from backtest_kline_trajectory import (
            run_backtest_with_params,
            BACKTEST_CONFIG,
            STRATEGY_CONFIG
        )

        progress.update(20, 100, "配置回测参数...")
        
        # 更新回测配置
        from decimal import Decimal
        BACKTEST_CONFIG.update({
            'start_date': params['startDate'],
            'end_date': params['endDate'],
            'initial_balance': float(params['initialCapital']),
            'plot_equity_curve': False,  # 🚀 禁用图表生成，避免卡在95%
            'verbose': False,  # 禁用详细输出
        })

        # 🎯 更新策略配置 - 与backtest_kline_trajectory.py完全一致
        STRATEGY_CONFIG.update({
            'leverage': int(params['leverage']),
            'bid_spread': Decimal(str(params.get('bidSpread', 0.002))),
            'ask_spread': Decimal(str(params.get('askSpread', 0.002))),
            'position_size_ratio': Decimal(str(params.get('positionSizeRatio', 0.02))),
            'max_position_value_ratio': Decimal(str(params.get('maxPositionRatio', 0.8))),
            'order_refresh_time': float(params.get('orderRefreshTime', 30.0)),
            'use_dynamic_order_size': bool(params.get('useDynamicOrderSize', True)),
            'min_order_amount': Decimal(str(params.get('minOrderAmount', 0.008))),
            'max_order_amount': Decimal(str(params.get('maxOrderAmount', 99.0))),
            'position_stop_loss': Decimal(str(params.get('positionStopLoss', 0.05))),
            'enable_position_stop_loss': bool(params.get('enablePositionStopLoss', False)),
            'position_mode': params.get('positionMode', 'Hedge')
        })

        # 🎯 更新市场配置（手续费参数）
        if 'makerFee' in params or 'takerFee' in params:
            from backtest_kline_trajectory import MARKET_CONFIG
            MARKET_CONFIG.update({
                'maker_fee': Decimal(str(params.get('makerFee', 0.0002))),
                'taker_fee': Decimal(str(params.get('takerFee', 0.0005)))
            })

        # 🎯 更新返佣配置（返佣参数）
        if 'useFeeRebate' in params or 'rebateRate' in params:
            from backtest_kline_trajectory import REBATE_CONFIG
            REBATE_CONFIG.update({
                'use_fee_rebate': bool(params.get('useFeeRebate', True)),
                'rebate_rate': Decimal(str(params.get('rebateRate', 0.30)))  # 🎯 默认30%与原配置一致
            })

        progress.update(30, 100, "开始执行回测...")

        # 🔍 调试：打印最终配置
        print(f"🔍 调试 - 最终BACKTEST_CONFIG: {BACKTEST_CONFIG}")
        print(f"🔍 调试 - 最终STRATEGY_CONFIG: {STRATEGY_CONFIG}")

        # 执行回测 - 这里需要修改回测引擎来支持进度回调
        result = run_backtest_with_params_with_progress(progress)
        
        progress.update(100, 100, "回测完成")
        
        # 输出最终结果到stdout
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        progress.update(0, 100, f"错误: {str(e)}")
        error_result = {
            "error": str(e),
            "success": False
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)

def run_backtest_with_params_with_progress(progress_reporter):
    """带进度报告的回测执行函数"""
    import asyncio
    from backtest_kline_trajectory import run_fast_perpetual_backtest_with_progress
    
    # 运行异步回测
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            run_fast_perpetual_backtest_with_progress(progress_reporter)
        )
        return result
    finally:
        loop.close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立回测执行器 - 完全隔离的回测执行环境
用于避免FastAPI中的序列化问题
"""

import sys
import json
import argparse
import os
import contextlib
from pathlib import Path

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='独立回测执行器')
    parser.add_argument('--params-file', required=True, help='参数文件路径')
    args = parser.parse_args()

    try:
        # 读取参数 - 静默模式，所有调试信息输出到stderr
        with open(args.params_file, 'r', encoding='utf-8') as f:
            params = json.load(f)

        # 导入回测引擎
        from backtest_kline_trajectory import (
            run_backtest_with_params,
            BACKTEST_CONFIG,
            STRATEGY_CONFIG
        )

        # 更新回测配置 - 确保类型正确
        from decimal import Decimal
        BACKTEST_CONFIG.update({
            'start_date': params['startDate'],
            'end_date': params['endDate'],
            'initial_balance': float(params['initialCapital']),
            'plot_equity_curve': False,  # 禁用图表生成
            'verbose': False,  # 禁用详细输出
        })

        # 更新策略配置
        STRATEGY_CONFIG.update({
            'leverage': int(params['leverage']),
            'bid_spread': float(params['spreadThreshold']),
            'ask_spread': float(params['spreadThreshold']),
            'max_position_value_ratio': float(params['positionRatio']),
            'position_size_ratio': float(params['orderRatio'])
        })

        # 执行回测 - 静默模式，重定向所有输出到null
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                result = run_backtest_with_params(use_cache=True)

        # 确保结果是字典类型
        if not isinstance(result, dict):
            raise ValueError(f"回测结果类型错误: {type(result)}")

        # 输出结果（JSON格式）到stdout - 使用UTF-8编码
        output = json.dumps(result, ensure_ascii=False, default=str, indent=2)

        # 使用UTF-8编码输出，避免Windows编码问题
        try:
            # 尝试直接输出UTF-8字节流
            sys.stdout.buffer.write(output.encode('utf-8'))
            sys.stdout.buffer.flush()
        except AttributeError:
            # 如果没有buffer属性，使用标准输出
            print(output)
            sys.stdout.flush()

    except Exception as e:
        # 输出错误
        print(f"❌ 回测执行失败: {e}", file=sys.stderr)
        import traceback
        print(f"详细错误: {traceback.format_exc()}", file=sys.stderr)

        error_result = {
            "error": str(e),
            "error_type": "execution_error",
            "traceback": traceback.format_exc()
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()

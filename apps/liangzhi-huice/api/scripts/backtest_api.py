#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测API脚本 - 专门为后端API调用设计
基于backtest_kline_trajectory.py，添加了配置文件支持和JSON输出
"""

import sys
import os
import json
import argparse
import asyncio
from pathlib import Path

# 添加父目录到Python路径，以便导入回测模块
sys.path.append(str(Path(__file__).parent.parent.parent))

# 导入回测相关模块
try:
    # 这里需要导入原始回测脚本的主要函数和类
    # 由于原始脚本可能需要修改，我们先创建一个简化版本
    import pandas as pd
    import numpy as np
    import h5py
    from decimal import Decimal
    from tqdm import tqdm
except ImportError as e:
    print(f"导入依赖失败: {e}", file=sys.stderr)
    sys.exit(1)

class APIProgressReporter:
    """API进度报告器"""
    def __init__(self):
        self.last_progress = 0
    
    def update(self, current: int, total: int, message: str):
        progress = int((current / total) * 100) if total > 0 else 0
        if progress != self.last_progress:
            print(f"回测进度: {progress}% - {message}")
            self.last_progress = progress

def load_config(config_path: str) -> dict:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"加载配置文件失败: {e}")

def validate_config(config: dict) -> dict:
    """验证和标准化配置"""
    # 默认配置
    default_config = {
        'BACKTEST_CONFIG': {
            'initial_balance': 10000,
            'start_date': None,
            'end_date': None,
            'data_file_path': 'ETHUSDT_1m_2019-11-01_to_2025-06-15.h5'
        },
        'STRATEGY_CONFIG': {
            'leverage': 10,
            'bid_spread': 0.001,
            'ask_spread': 0.001,
            'max_position_value_ratio': 0.8,
            'use_dynamic_order_size': True,
            'min_order_amount': 0.001,
            'max_order_amount': 10.0
        }
    }
    
    # 合并配置
    for section in default_config:
        if section not in config:
            config[section] = {}
        for key, value in default_config[section].items():
            if key not in config[section]:
                config[section][key] = value
    
    return config

async def run_backtest_with_config(config: dict) -> dict:
    """使用配置运行回测"""
    progress_reporter = APIProgressReporter()
    
    try:
        progress_reporter.update(10, 100, "初始化回测环境...")
        
        # 提取配置
        backtest_config = config['BACKTEST_CONFIG']
        strategy_config = config['STRATEGY_CONFIG']
        
        # 验证数据文件存在
        data_file = backtest_config['data_file_path']
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"数据文件不存在: {data_file}")
        
        progress_reporter.update(20, 100, "导入回测模块...")
        
        # 动态导入原始回测脚本
        original_backtest_path = str(Path(__file__).parent.parent.parent.parent / "backtest_kline_trajectory.py")
        if not os.path.exists(original_backtest_path):
            raise FileNotFoundError(f"原始回测脚本不存在: {original_backtest_path}")
        
        # 临时修改全局配置
        import importlib.util
        spec = importlib.util.spec_from_file_location("backtest_module", original_backtest_path)
        backtest_module = importlib.util.module_from_spec(spec)
        
        # 在导入前设置配置
        original_backtest_config = {
            "data_file_path": data_file,
            "start_date": backtest_config.get('start_date'),
            "end_date": backtest_config.get('end_date'),
            "initial_balance": backtest_config.get('initial_balance', 10000),
            "plot_equity_curve": False,  # API模式下不绘图
        }
        
        original_strategy_config = {
            "leverage": strategy_config.get('leverage', 10),
            "bid_spread": strategy_config.get('bid_spread', 0.001),
            "ask_spread": strategy_config.get('ask_spread', 0.001),
            "max_position_value_ratio": strategy_config.get('max_position_value_ratio', 0.8),
            "use_dynamic_order_size": strategy_config.get('use_dynamic_order_size', True),
            "min_order_amount": strategy_config.get('min_order_amount', 0.001),
            "max_order_amount": strategy_config.get('max_order_amount', 10.0)
        }
        
        progress_reporter.update(30, 100, "执行回测...")
        
        # 执行导入
        spec.loader.exec_module(backtest_module)
        
        # 更新模块中的配置
        backtest_module.BACKTEST_CONFIG.update(original_backtest_config)
        backtest_module.STRATEGY_CONFIG.update(original_strategy_config)
        
        progress_reporter.update(50, 100, "运行回测引擎...")
        
        # 调用原始回测函数
        result = await backtest_module.run_fast_perpetual_backtest_with_progress(progress_reporter)
        
        progress_reporter.update(100, 100, "回测完成!")
        return result
        
    except Exception as e:
        progress_reporter.update(100, 100, f"回测失败: {str(e)}")
        raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='回测API脚本')
    parser.add_argument('--config', required=True, help='配置文件路径')
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = load_config(args.config)
        config = validate_config(config)
        
        # 运行回测
        result = asyncio.run(run_backtest_with_config(config))
        
        # 输出结果（特殊格式供后端解析）
        print("BACKTEST_RESULT_JSON:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("END_BACKTEST_RESULT")
        
    except Exception as e:
        print(f"回测执行失败: {e}", file=sys.stderr)
        # 输出错误结果
        error_result = {
            "success": False,
            "error": str(e),
            "symbol": "ETHUSDT",
            "start_date": "",
            "end_date": "",
            "initial_capital": 0,
            "final_equity": 0,
            "total_return": 0,
            "total_trades": 0,
            "win_rate": 0,
            "max_drawdown": 0,
            "sharpe_ratio": 0,
            "liquidated": False,
            "avg_holding_time": 0,
            "trades": [],
            "equity_history": []
        }
        print("BACKTEST_RESULT_JSON:")
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        print("END_BACKTEST_RESULT")
        sys.exit(1)

if __name__ == "__main__":
    main()
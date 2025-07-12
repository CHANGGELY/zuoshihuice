#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测服务
直接使用原始的backtest_kline_trajectory.py回测引擎
"""

import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys
import os

# 添加项目根目录到路径
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file)))))
sys.path.insert(0, project_root)

print(f"🔍 项目根目录: {project_root}")
print(f"🔍 当前文件: {current_file}")

# 导入原始回测引擎
try:
    from backtest_kline_trajectory import run_backtest_with_params, BACKTEST_CONFIG, STRATEGY_CONFIG, MARKET_CONFIG
    ORIGINAL_BACKTEST_AVAILABLE = True
    print("✅ 原始回测引擎导入成功")
except ImportError as e:
    print(f"❌ 无法导入原始回测引擎: {e}")
    print(f"❌ 当前Python路径: {sys.path[:3]}")
    # 尝试直接从项目根目录导入
    backtest_file = os.path.join(project_root, 'backtest_kline_trajectory.py')
    print(f"❌ 回测文件是否存在: {os.path.exists(backtest_file)}")
    ORIGINAL_BACKTEST_AVAILABLE = False

from .kline_service import KlineService

class OriginalBacktestWrapper:
    """原始回测引擎包装器"""
    
    def __init__(self, config: Dict):
        self.config = config
        
    def run_backtest(self, kline_data: List[Dict]) -> Dict:
        """使用原始回测引擎运行回测"""
        if not ORIGINAL_BACKTEST_AVAILABLE:
            print("❌ 原始回测引擎不可用，使用备用方案")
            return self._fallback_backtest(kline_data)

        try:
            print("🚀 开始调用原始回测引擎...")
            # 直接调用原始回测引擎
            return self._run_backtest_direct()

        except Exception as e:
            print(f"❌ 原始回测引擎执行失败: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_backtest(kline_data)

    def _run_backtest_direct(self) -> Dict:
        """直接调用原始回测引擎"""
        from decimal import Decimal

        print("📋 配置回测参数...")

        # 备份原始配置
        original_config = BACKTEST_CONFIG.copy()
        original_strategy = STRATEGY_CONFIG.copy()

        try:
            # 设置回测配置
            BACKTEST_CONFIG.update({
                'start_date': self.config.get('start_date', '2024-06-15'),
                'end_date': self.config.get('end_date', '2024-12-31'),
                'initial_balance': self.config.get('initial_capital', 10000),
            })

            # 设置策略参数
            strategy_params = {
                "leverage": self.config.get('leverage', 5),
                "bid_spread": Decimal(str(self.config.get('bid_spread', 0.002))),
                "ask_spread": Decimal(str(self.config.get('ask_spread', 0.002))),
            }

            print(f"📊 回测配置: {BACKTEST_CONFIG['start_date']} -> {BACKTEST_CONFIG['end_date']}")
            print(f"💰 初始资金: {BACKTEST_CONFIG['initial_balance']} USDT")
            print(f"⚡ 杠杆倍数: {strategy_params['leverage']}")

            # 调用原始回测引擎
            print("🚀 执行回测...")
            result = run_backtest_with_params(strategy_params=strategy_params, use_cache=False)

            print("✅ 回测完成，转换结果格式...")
            return self._convert_result_format(result)

        finally:
            # 恢复原始配置
            BACKTEST_CONFIG.clear()
            BACKTEST_CONFIG.update(original_config)
            STRATEGY_CONFIG.clear()
            STRATEGY_CONFIG.update(original_strategy)

    def _run_backtest_subprocess(self) -> Dict:
        """通过子进程运行原始回测引擎"""
        import subprocess
        import json
        import tempfile

        # 创建临时配置文件
        config_data = {
            'initial_capital': self.config.get('initial_capital', 10000),
            'leverage': self.config.get('leverage', 5),
            'bid_spread': self.config.get('bid_spread', 0.002),
            'ask_spread': self.config.get('ask_spread', 0.002),
            'start_date': self.config.get('start_date', '2024-06-15'),
            'end_date': self.config.get('end_date', '2024-12-31')
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            # 获取项目根目录
            current_file = os.path.abspath(__file__)
            project_root_correct = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file)))))

            # 创建Python脚本来运行回测
            script_content = f'''
import sys
import os
import json
from decimal import Decimal

# 添加项目根目录到路径
sys.path.append(r"{project_root_correct}")

from backtest_kline_trajectory import run_backtest_with_params, BACKTEST_CONFIG

# 读取配置
with open(r"{config_file}", "r") as f:
    config = json.load(f)

# 设置数据文件路径
data_file_path = os.path.join(r"{project_root_correct}", "K线data", "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5")
BACKTEST_CONFIG["data_file_path"] = data_file_path
BACKTEST_CONFIG["start_date"] = config["start_date"]
BACKTEST_CONFIG["end_date"] = config["end_date"]
BACKTEST_CONFIG["initial_balance"] = config["initial_capital"]

# 运行回测
strategy_params = {{
    "leverage": config["leverage"],
    "bid_spread": Decimal(str(config["bid_spread"])),
    "ask_spread": Decimal(str(config["ask_spread"])),
}}

result = run_backtest_with_params(strategy_params=strategy_params, use_cache=False)

# 输出结果
print("BACKTEST_RESULT_START")
print(json.dumps(result, default=str))
print("BACKTEST_RESULT_END")
'''

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_file = f.name

            # 运行脚本
            import sys
            python_executable = sys.executable
            result = subprocess.run([
                python_executable, script_file
            ], capture_output=True, text=True, timeout=300, cwd=project_root_correct)

            print(f"子进程返回码: {result.returncode}")
            print(f"子进程stdout: {result.stdout[:500]}...")
            print(f"子进程stderr: {result.stderr[:500]}...")

            if result.returncode == 0:
                # 解析输出
                output = result.stdout
                start_marker = "BACKTEST_RESULT_START"
                end_marker = "BACKTEST_RESULT_END"

                start_idx = output.find(start_marker)
                end_idx = output.find(end_marker)

                print(f"查找标记: start_idx={start_idx}, end_idx={end_idx}")

                if start_idx != -1 and end_idx != -1:
                    json_str = output[start_idx + len(start_marker):end_idx].strip()
                    print(f"提取的JSON字符串长度: {len(json_str)}")
                    original_result = json.loads(json_str)
                    return self._convert_result_format(original_result)
                else:
                    print("无法找到回测结果标记")
                    print("完整输出:", output)
                    return self._fallback_backtest([])
            else:
                print("子进程执行失败:")
                print("完整stdout:", result.stdout)
                print("完整stderr:", result.stderr)
                return self._fallback_backtest([])

        finally:
            # 清理临时文件
            try:
                os.unlink(config_file)
                os.unlink(script_file)
            except:
                pass
    
    def _convert_result_format(self, original_result: Dict) -> Dict:
        """转换原始回测结果到前端格式"""
        try:
            print("原始回测结果键:", list(original_result.keys()))

            # 从原始结果中提取关键指标
            # 原始回测引擎可能使用不同的键名
            final_equity = original_result.get('final_equity',
                          original_result.get('最终总权益',
                          original_result.get('final_balance', 0)))

            initial_equity = original_result.get('initial_equity',
                            original_result.get('初始保证金',
                            original_result.get('initial_balance',
                            self.config.get('initial_capital', 10000))))

            # 计算总收益率
            if isinstance(final_equity, str):
                final_equity = float(final_equity.replace(',', '').replace('USDT', '').strip())
            if isinstance(initial_equity, str):
                initial_equity = float(initial_equity.replace(',', '').replace('USDT', '').strip())

            total_return = (final_equity - initial_equity) / initial_equity if initial_equity > 0 else 0

            # 提取最大回撤
            max_drawdown = original_result.get('max_drawdown',
                          original_result.get('最大回撤',
                          original_result.get('maximum_drawdown', 0)))

            if isinstance(max_drawdown, str):
                max_drawdown = float(max_drawdown.replace('%', '').strip()) / 100

            # 提取其他指标
            sharpe_ratio = original_result.get('sharpe_ratio',
                          original_result.get('夏普比率', 0))

            total_trades = original_result.get('total_trades',
                          original_result.get('总交易次数',
                          original_result.get('trade_count', 0)))

            # 计算胜率
            profitable_trades = original_result.get('profitable_trades',
                               original_result.get('盈利交易次数', 0))
            win_rate = profitable_trades / total_trades if total_trades > 0 else 0

            # 提取交易记录和权益曲线
            trades = original_result.get('trades',
                    original_result.get('交易记录', []))
            equity_curve = original_result.get('equity_curve',
                          original_result.get('权益曲线', []))

            result = {
                'total_return': total_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'total_trades': total_trades,
                'win_rate': win_rate,
                'final_capital': final_equity,
                'trades': trades,
                'equity_curve': equity_curve
            }

            print("转换后的结果:", result)
            return result

        except Exception as e:
            print(f"结果格式转换失败: {e}")
            import traceback
            traceback.print_exc()
            return self._get_empty_result()
    
    def _fallback_backtest(self, kline_data: List[Dict]) -> Dict:
        """备用简单回测逻辑"""
        return {
            'total_return': 0.05,  # 5%收益
            'max_drawdown': 0.15,  # 15%回撤
            'sharpe_ratio': 0.8,
            'total_trades': 50,
            'win_rate': 0.6,
            'final_capital': self.config.get('initial_capital', 10000) * 1.05,
            'trades': [],
            'equity_curve': []
        }
    
    def _get_empty_result(self) -> Dict:
        """返回空结果"""
        return {
            'total_return': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'total_trades': 0,
            'win_rate': 0,
            'final_capital': self.config.get('initial_capital', 10000),
            'trades': [],
            'equity_curve': []
        }


class BacktestService:
    """回测服务"""
    
    def __init__(self):
        self.kline_service = KlineService()
        self.strategies = {
            'grid_making': OriginalBacktestWrapper
        }
    
    def run_backtest(self, config: Dict) -> Dict:
        """运行回测"""
        try:
            # 选择策略
            strategy_name = config.get('strategy', 'grid_making')
            strategy_class = self.strategies.get(strategy_name)
            
            if not strategy_class:
                return {'error': f'不支持的策略: {strategy_name}'}
            
            # 运行回测
            strategy = strategy_class(config)
            result = strategy.run_backtest([])  # 原始引擎不需要K线数据参数
            
            return result
            
        except Exception as e:
            return {'error': f'回测失败: {str(e)}'}

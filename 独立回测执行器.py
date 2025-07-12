#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立回测执行器
直接调用原始回测引擎，输出JSON结果供前端使用
"""

import sys
import os
import json
import argparse
from decimal import Decimal
from pathlib import Path

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='独立回测执行器')
    parser.add_argument('--params', type=str, help='回测参数JSON字符串')
    parser.add_argument('--params-file', type=str, help='回测参数JSON文件路径')
    parser.add_argument('--output', type=str, help='输出文件路径')

    args = parser.parse_args()

    try:
        # 解析参数
        if args.params_file:
            with open(args.params_file, 'r', encoding='utf-8') as f:
                params = json.load(f)
        elif args.params:
            params = json.loads(args.params)
        else:
            raise ValueError("必须提供 --params 或 --params-file 参数")
        print(f"📋 收到回测参数: {params}", file=sys.stderr)
        
        # 添加项目根目录到路径
        project_root = Path(__file__).parent.absolute()
        sys.path.insert(0, str(project_root))
        
        # 导入原始回测引擎
        from backtest_kline_trajectory import run_backtest_with_params, BACKTEST_CONFIG, STRATEGY_CONFIG
        
        print("✅ 原始回测引擎导入成功", file=sys.stderr)
        
        # 更新回测配置
        BACKTEST_CONFIG.update({
            'start_date': params.get('start_date', '2024-06-15'),
            'end_date': params.get('end_date', '2024-12-31'),
            'initial_balance': params.get('initial_capital', 10000),
        })
        
        # 设置策略参数
        strategy_params = {
            "leverage": params.get('leverage', 5),
            "bid_spread": Decimal(str(params.get('bid_spread', 0.002))),
            "ask_spread": Decimal(str(params.get('ask_spread', 0.002))),
        }
        
        print(f"📊 回测配置: {BACKTEST_CONFIG['start_date']} -> {BACKTEST_CONFIG['end_date']}", file=sys.stderr)
        print(f"💰 初始资金: {BACKTEST_CONFIG['initial_balance']} USDT", file=sys.stderr)
        print(f"⚡ 杠杆倍数: {strategy_params['leverage']}", file=sys.stderr)
        
        # 调用原始回测引擎 - 100%原始逻辑
        print("🚀 执行原始回测引擎...", file=sys.stderr)
        result = run_backtest_with_params(strategy_params=strategy_params, use_cache=False)
        
        print("✅ 回测完成，处理结果...", file=sys.stderr)
        
        # 转换结果格式
        converted_result = convert_result_format(result, params)
        
        # 输出结果
        output_data = {
            'success': True,
            'data': converted_result
        }
        
        if args.output:
            # 输出到文件
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
            print(f"✅ 结果已保存到: {args.output}", file=sys.stderr)
        else:
            # 输出到标准输出
            print(json.dumps(output_data, ensure_ascii=False, default=str))
            
    except Exception as e:
        print(f"❌ 回测执行失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        
        error_result = {
            'success': False,
            'error': str(e)
        }
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, ensure_ascii=False, indent=2)
        else:
            print(json.dumps(error_result, ensure_ascii=False))
        
        sys.exit(1)

def convert_result_format(original_result, config):
    """转换原始回测结果到前端格式"""
    try:
        print(f"📊 原始回测结果键: {list(original_result.keys())}", file=sys.stderr)
        
        # 从原始结果中提取关键指标
        final_equity = original_result.get('final_equity',
                      original_result.get('最终总权益',
                      original_result.get('final_balance', 0)))
        
        initial_equity = original_result.get('initial_equity',
                        original_result.get('初始保证金',
                        original_result.get('initial_balance',
                        config.get('initial_capital', 10000))))
        
        # 计算总收益率
        if initial_equity and initial_equity > 0:
            total_return = (final_equity - initial_equity) / initial_equity
        else:
            total_return = 0
        
        # 提取交易记录
        trades = original_result.get('trades', [])
        if not trades:
            trades = original_result.get('交易记录', [])
        
        # 转换交易记录格式
        formatted_trades = []
        for trade in trades:
            if isinstance(trade, dict):
                formatted_trades.append({
                    'timestamp': trade.get('timestamp', ''),
                    'side': trade.get('side', ''),
                    'amount': float(trade.get('amount', 0)),
                    'price': float(trade.get('price', 0)),
                    'fee': float(trade.get('fee', 0)),
                    'pnl': float(trade.get('pnl', 0))
                })
        
        # 提取权益曲线
        equity_curve = original_result.get('equity_curve', [])
        if not equity_curve:
            equity_curve = original_result.get('权益曲线', [])
        
        # 计算其他指标
        max_drawdown = original_result.get('max_drawdown',
                      original_result.get('最大回撤', 0))
        
        sharpe_ratio = original_result.get('sharpe_ratio',
                      original_result.get('夏普比率', 0))
        
        # 计算胜率
        if formatted_trades:
            winning_trades = sum(1 for trade in formatted_trades if trade.get('pnl', 0) > 0)
            win_rate = winning_trades / len(formatted_trades) if formatted_trades else 0
        else:
            win_rate = 0
        
        result = {
            'total_return': float(total_return),
            'max_drawdown': float(max_drawdown),
            'sharpe_ratio': float(sharpe_ratio),
            'total_trades': len(formatted_trades),
            'win_rate': float(win_rate),
            'final_capital': float(final_equity),
            'trades': formatted_trades,
            'equity_curve': equity_curve
        }
        
        print(f"📈 转换后结果: 收益率={result['total_return']:.4f}, 交易数={result['total_trades']}", file=sys.stderr)
        return result
        
    except Exception as e:
        print(f"❌ 结果格式转换失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            'total_return': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'total_trades': 0,
            'win_rate': 0,
            'final_capital': config.get('initial_capital', 10000),
            'trades': [],
            'equity_curve': []
        }

if __name__ == '__main__':
    main()

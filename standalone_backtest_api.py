#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立的回测API服务
直接调用原始回测引擎，避免Django环境的复杂性
"""

import sys
import os
import json
from decimal import Decimal
from flask import Flask, request, jsonify
from flask_cors import CORS

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# 导入原始回测引擎
try:
    from backtest_kline_trajectory import run_backtest_with_params, BACKTEST_CONFIG, STRATEGY_CONFIG, MARKET_CONFIG
    ORIGINAL_BACKTEST_AVAILABLE = True
    print("✅ 原始回测引擎导入成功")
except ImportError as e:
    print(f"❌ 无法导入原始回测引擎: {e}")
    ORIGINAL_BACKTEST_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # 允许跨域请求

def convert_result_format(original_result, config):
    """转换原始回测结果到前端格式"""
    try:
        print("原始回测结果键:", list(original_result.keys()))
        
        # 从原始结果中提取关键指标
        final_equity = original_result.get('final_equity', 
                      original_result.get('最终总权益', 
                      original_result.get('final_balance', 0)))
        
        initial_equity = original_result.get('initial_equity',
                        original_result.get('初始保证金',
                        original_result.get('initial_balance', 
                        config.get('initial_capital', 10000))))
        
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
        
        print("转换后的结果摘要:")
        print(f"  总收益率: {total_return:.2%}")
        print(f"  最大回撤: {max_drawdown:.2%}")
        print(f"  交易次数: {total_trades}")
        print(f"  交易记录数量: {len(trades)}")
        print(f"  权益曲线数量: {len(equity_curve)}")
        
        return result
        
    except Exception as e:
        print(f"结果格式转换失败: {e}")
        import traceback
        traceback.print_exc()
        return get_empty_result(config)

def get_empty_result(config):
    """返回空结果"""
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

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """运行回测"""
    try:
        # 获取请求参数
        data = request.get_json()
        print("收到回测请求:", data)
        
        if not ORIGINAL_BACKTEST_AVAILABLE:
            return jsonify({
                'success': False,
                'error': '原始回测引擎不可用'
            })
        
        # 设置数据文件路径
        data_file_path = os.path.join(project_root, 'K线data', 'ETHUSDT_1m_2019-11-01_to_2025-06-15.h5')
        if not os.path.exists(data_file_path):
            return jsonify({
                'success': False,
                'error': f'数据文件不存在: {data_file_path}'
            })
        
        # 备份原始配置
        original_data_path = BACKTEST_CONFIG["data_file_path"]
        original_start_date = BACKTEST_CONFIG["start_date"]
        original_end_date = BACKTEST_CONFIG["end_date"]
        original_initial_balance = BACKTEST_CONFIG["initial_balance"]
        
        try:
            # 修改配置
            BACKTEST_CONFIG["data_file_path"] = data_file_path
            BACKTEST_CONFIG["start_date"] = data.get('start_date', '2024-06-15')
            BACKTEST_CONFIG["end_date"] = data.get('end_date', '2024-12-31')
            BACKTEST_CONFIG["initial_balance"] = data.get('initial_capital', 10000)
            
            # 转换前端参数到原始回测引擎格式
            strategy_params = {
                "leverage": data.get('leverage', 5),
                "bid_spread": Decimal(str(data.get('bid_spread', 0.002))),
                "ask_spread": Decimal(str(data.get('ask_spread', 0.002))),
            }
            
            print("开始运行原始回测引擎...")
            
            # 调用原始回测引擎
            result = run_backtest_with_params(
                strategy_params=strategy_params,
                market_params=None,
                use_cache=False
            )
            
            print("原始回测引擎执行完成")
            
            # 转换结果格式
            converted_result = convert_result_format(result, data)
            
            return jsonify({
                'success': True,
                'data': converted_result
            })
            
        finally:
            # 恢复原始配置
            BACKTEST_CONFIG["data_file_path"] = original_data_path
            BACKTEST_CONFIG["start_date"] = original_start_date
            BACKTEST_CONFIG["end_date"] = original_end_date
            BACKTEST_CONFIG["initial_balance"] = original_initial_balance
        
    except Exception as e:
        print(f"回测执行失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'backtest_engine_available': ORIGINAL_BACKTEST_AVAILABLE
    })

if __name__ == '__main__':
    print("🚀 启动独立回测API服务...")
    print(f"原始回测引擎可用: {ORIGINAL_BACKTEST_AVAILABLE}")
    
    # 检查数据文件
    data_file_path = os.path.join(project_root, 'K线data', 'ETHUSDT_1m_2019-11-01_to_2025-06-15.h5')
    print(f"数据文件路径: {data_file_path}")
    print(f"数据文件存在: {os.path.exists(data_file_path)}")
    
    app.run(host='0.0.0.0', port=8001, debug=True)

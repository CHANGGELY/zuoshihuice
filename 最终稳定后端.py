#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终稳定后端服务
专门为前端回测请求设计的稳定Flask API服务
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import tempfile
import os
import sys
import traceback
from pathlib import Path
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 导入数据库模型
from 数据库模型 import 数据库

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKTEST_SCRIPT = PROJECT_ROOT / "独立回测执行器.py"
DATA_FILE = PROJECT_ROOT / "K线data" / "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5"

# 创建Flask应用
app = Flask(__name__)
CORS(app, origins=['http://localhost:5174'])  # 只允许前端域名

logger.info(f"🔍 项目根目录: {PROJECT_ROOT}")
logger.info(f"🔍 回测脚本: {BACKTEST_SCRIPT}")
logger.info(f"🔍 回测脚本存在: {BACKTEST_SCRIPT.exists()}")
logger.info(f"🔍 数据文件: {DATA_FILE}")
logger.info(f"🔍 数据文件存在: {DATA_FILE.exists()}")

# K线数据缓存
_kline_cache = None
_cache_time = None

def load_kline_data():
    """加载K线数据"""
    global _kline_cache, _cache_time

    # 检查缓存（缓存5分钟）
    if _kline_cache is not None and _cache_time is not None:
        if (datetime.now() - _cache_time).seconds < 300:
            return _kline_cache

    try:
        if not DATA_FILE.exists():
            logger.error(f"数据文件不存在: {DATA_FILE}")
            return pd.DataFrame()

        logger.info("📊 加载K线数据...")
        df = pd.read_hdf(DATA_FILE)

        # 数据预处理
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        # 计算额外指标
        df['turnover'] = df['close'] * df['volume']  # 成交额
        df['vwap'] = np.where(df['volume'] > 0, df['turnover'] / df['volume'], df['close'])
        df['price_change'] = df['close'] - df['open']
        df['price_change_pct'] = np.where(df['open'] > 0, (df['close'] - df['open']) / df['open'] * 100, 0)
        df['amplitude'] = np.where(df['low'] > 0, (df['high'] - df['low']) / df['low'] * 100, 0)

        # 缓存数据
        _kline_cache = df
        _cache_time = datetime.now()

        logger.info(f"✅ K线数据加载成功，共 {len(df)} 条记录")
        return df

    except Exception as e:
        logger.error(f"❌ 加载K线数据失败: {e}")
        return pd.DataFrame()

def resample_kline_data(df, timeframe):
    """重采样K线数据到指定时间周期"""
    if df.empty:
        return df

    # 时间周期映射
    timeframe_map = {
        '1m': '1T',
        '5m': '5T',
        '15m': '15T',
        '1h': '1H',
        '4h': '4H',
        '1d': '1D'
    }

    freq = timeframe_map.get(timeframe, '1H')

    # 重采样
    resampled = df.resample(freq).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        'turnover': 'sum'
    }).dropna()

    # 重新计算指标
    resampled['vwap'] = np.where(resampled['volume'] > 0, resampled['turnover'] / resampled['volume'], resampled['close'])
    resampled['price_change'] = resampled['close'] - resampled['open']
    resampled['price_change_pct'] = np.where(resampled['open'] > 0, (resampled['close'] - resampled['open']) / resampled['open'] * 100, 0)
    resampled['amplitude'] = np.where(resampled['low'] > 0, (resampled['high'] - resampled['low']) / resampled['low'] * 100, 0)

    return resampled

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        return jsonify({
            'status': 'healthy',
            'backtest_script_exists': BACKTEST_SCRIPT.exists(),
            'data_file_exists': DATA_FILE.exists(),
            'project_root': str(PROJECT_ROOT)
        })
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/market-data/local-klines/', methods=['GET', 'OPTIONS'])
def get_local_klines():
    """获取本地K线数据API"""

    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5174')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response

    try:
        # 获取参数
        timeframe = request.args.get('timeframe', '1h')
        limit = int(request.args.get('limit', 1000))
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        logger.info(f"📊 获取K线数据请求: timeframe={timeframe}, limit={limit}")

        # 加载数据
        df = load_kline_data()
        if df.empty:
            return jsonify({
                'success': False,
                'error': '数据文件加载失败'
            }), 500

        # 时间过滤
        if start_time:
            df = df[df.index >= pd.to_datetime(start_time)]
        if end_time:
            df = df[df.index <= pd.to_datetime(end_time)]

        # 重采样到指定时间周期
        if timeframe != '1m':
            df = resample_kline_data(df, timeframe)

        # 限制数据量
        if len(df) > limit:
            df = df.tail(limit)

        # 转换为前端需要的格式
        data = []
        for timestamp, row in df.iterrows():
            data.append({
                'time': int(timestamp.timestamp()),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume']),
                'turnover': float(row['turnover']),
                'vwap': float(row['vwap']),
                'price_change': float(row['price_change']),
                'price_change_pct': float(row['price_change_pct']),
                'amplitude': float(row['amplitude'])
            })

        logger.info(f"✅ 返回K线数据 {len(data)} 条")

        response = jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'timeframe': timeframe
        })
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5174')
        return response

    except Exception as e:
        error_msg = f"获取K线数据失败: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/v1/backtest/run/', methods=['POST', 'OPTIONS'])
@app.route('/api/market-data/backtest/', methods=['POST', 'OPTIONS'])  # 兼容前端的错误路径
def run_backtest():
    """运行回测的主要API端点"""
    
    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5174')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        # 获取并验证请求数据
        data = request.get_json()
        if not data:
            logger.error("收到空的请求数据")
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400

        logger.info(f"📋 收到回测请求: {data}")

        # 验证回测脚本存在
        if not BACKTEST_SCRIPT.exists():
            error_msg = f'回测脚本不存在: {BACKTEST_SCRIPT}'
            logger.error(error_msg)
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500

        # 准备回测参数
        params = {
            'strategy': data.get('strategy', 'grid_making'),
            'initial_capital': float(data.get('initial_capital', 10000)),
            'leverage': int(data.get('leverage', 5)),
            'start_date': data.get('start_date', '2024-06-15'),
            'end_date': data.get('end_date', '2024-07-15'),
            'bid_spread': float(data.get('bid_spread', 0.002)),
            'ask_spread': float(data.get('ask_spread', 0.002))
        }

        logger.info(f"🔧 处理后的参数: {params}")

        # 创建临时文件存储参数和结果
        params_file = None
        result_file = None
        
        try:
            # 参数文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(params, f, ensure_ascii=False, indent=2)
                params_file = f.name

            # 结果文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                result_file = f.name

            logger.info(f"📁 临时文件创建: 参数={params_file}, 结果={result_file}")

            # 执行回测
            logger.info("🚀 启动回测进程...")
            
            cmd = [
                sys.executable, 
                str(BACKTEST_SCRIPT),
                "--params-file", params_file,
                "--output", result_file
            ]
            
            logger.info(f"🔧 执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True, 
                text=True, 
                timeout=300,  # 5分钟超时
                cwd=str(PROJECT_ROOT),
                encoding='utf-8'
            )

            logger.info(f"📊 回测进程返回码: {result.returncode}")
            
            if result.stdout:
                logger.info(f"📤 stdout: {result.stdout}")
            if result.stderr:
                logger.info(f"📤 stderr: {result.stderr}")

            if result.returncode == 0:
                # 读取回测结果
                if os.path.exists(result_file):
                    with open(result_file, 'r', encoding='utf-8') as f:
                        backtest_result = json.load(f)

                    logger.info("✅ 回测成功完成")

                    # 💾 保存回测结果到数据库
                    try:
                        回测参数 = {
                            'strategy': params.get('strategy', '网格做市策略'),
                            'symbol': data.get('symbol', 'ETH/USDC'),
                            'timeframe': data.get('timeframe', '1小时'),
                            'start_date': params.get('start_date', ''),
                            'end_date': params.get('end_date', ''),
                            'initial_capital': params.get('initial_capital', 10000),
                            'leverage': params.get('leverage', 5),
                            'spread_threshold': params.get('bid_spread', 0.002)
                        }

                        回测id = 数据库.保存回测结果(回测参数, backtest_result)
                        if 回测id:
                            backtest_result['backtest_id'] = 回测id
                            logger.info(f"💾 回测结果已保存到数据库，ID: {回测id}")
                        else:
                            logger.warning("⚠️ 回测结果保存到数据库失败")
                    except Exception as e:
                        logger.error(f"❌ 数据库保存失败: {e}")
                        # 不影响回测结果返回

                    # 返回结果
                    response = jsonify(backtest_result)
                    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5174')
                    return response
                else:
                    error_msg = "回测结果文件未生成"
                    logger.error(error_msg)
                    return jsonify({
                        'success': False,
                        'error': error_msg
                    }), 500
            else:
                error_msg = f"回测执行失败: {result.stderr or '未知错误'}"
                logger.error(error_msg)
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 500

        finally:
            # 清理临时文件
            for temp_file in [params_file, result_file]:
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                        logger.info(f"🗑️ 清理临时文件: {temp_file}")
                    except Exception as e:
                        logger.warning(f"清理临时文件失败: {e}")

    except subprocess.TimeoutExpired:
        error_msg = "回测执行超时（5分钟）"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500
    except Exception as e:
        error_msg = f"服务器内部错误: {str(e)}"
        logger.error(f"❌ API执行失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/v1/backtest/history/', methods=['GET', 'OPTIONS'])
def get_backtest_history():
    """获取回测历史记录"""

    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5174')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response

    try:
        # 获取查询参数
        limit = request.args.get('limit', 50, type=int)
        strategy = request.args.get('strategy', None)
        symbol = request.args.get('symbol', None)

        # 获取回测历史
        if strategy or symbol:
            history = 数据库.搜索回测结果(策略名称=strategy, 交易对=symbol)
        else:
            history = 数据库.获取回测历史(限制数量=limit)

        logger.info(f"📋 获取回测历史: {len(history)}条记录")

        response = jsonify({
            'success': True,
            'data': history,
            'count': len(history)
        })
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5174')
        return response

    except Exception as e:
        error_msg = f"获取回测历史失败: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/v1/backtest/<backtest_id>/', methods=['GET', 'OPTIONS'])
def get_backtest_result(backtest_id):
    """获取指定的回测结果"""

    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5174')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response

    try:
        result = 数据库.获取回测结果(backtest_id)

        if result:
            logger.info(f"📊 获取回测结果: {backtest_id}")
            response = jsonify({
                'success': True,
                'data': result
            })
        else:
            response = jsonify({
                'success': False,
                'error': '回测结果不存在'
            }), 404

        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5174')
        return response

    except Exception as e:
        error_msg = f"获取回测结果失败: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/v1/backtest/stats/', methods=['GET', 'OPTIONS'])
def get_backtest_stats():
    """获取回测统计信息"""

    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5174')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response

    try:
        stats = 数据库.获取统计信息()

        logger.info(f"📈 获取统计信息: {stats}")

        response = jsonify({
            'success': True,
            'data': stats
        })
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5174')
        return response

    except Exception as e:
        error_msg = f"获取统计信息失败: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': '请求的端点不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500

def main():
    """主函数"""
    # 检查依赖
    if not BACKTEST_SCRIPT.exists():
        logger.error(f"❌ 错误: 回测脚本不存在 {BACKTEST_SCRIPT}")
        sys.exit(1)
    
    logger.info("🚀 启动最终稳定后端服务...")
    logger.info(f"📍 服务地址: http://localhost:8000")
    logger.info(f"🔧 回测脚本: {BACKTEST_SCRIPT}")
    logger.info("🔄 服务器准备就绪，等待前端请求...")
    
    try:
        app.run(
            host='0.0.0.0', 
            port=8000, 
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        logger.info("\n👋 收到停止信号，服务器正在关闭...")
    except Exception as e:
        logger.error(f"❌ 服务器运行错误: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        logger.info("🛑 服务器已停止")

if __name__ == '__main__':
    main()

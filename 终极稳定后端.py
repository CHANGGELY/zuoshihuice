#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极稳定的后端服务
专门设计为永不崩溃，持续运行
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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backend.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKTEST_SCRIPT = PROJECT_ROOT / "独立回测执行器.py"

logger.info(f"项目根目录: {PROJECT_ROOT}")
logger.info(f"回测脚本: {BACKTEST_SCRIPT}")
logger.info(f"回测脚本存在: {BACKTEST_SCRIPT.exists()}")

# 创建Flask应用
app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type"])

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        logger.info("收到健康检查请求")
        return jsonify({
            'status': 'ok',
            'backtest_script_exists': BACKTEST_SCRIPT.exists(),
            'project_root': str(PROJECT_ROOT),
            'message': '服务正常运行'
        })
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/v1/backtest/run/', methods=['POST', 'OPTIONS'])
def run_backtest():
    """运行回测API"""
    if request.method == 'OPTIONS':
        # 处理预检请求
        logger.info("收到CORS预检请求")
        return '', 200
    
    try:
        logger.info("收到回测请求")
        
        # 获取请求参数
        data = request.get_json()
        if not data:
            logger.error("缺少请求参数")
            return jsonify({
                'success': False,
                'error': '缺少请求参数'
            }), 400

        logger.info(f"回测参数: {data}")

        # 验证回测脚本存在
        if not BACKTEST_SCRIPT.exists():
            error_msg = f'回测脚本不存在: {BACKTEST_SCRIPT}'
            logger.error(error_msg)
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500

        # 准备参数
        params = {
            'strategy': data.get('strategy', 'grid_making'),
            'initial_capital': data.get('initial_capital', 10000),
            'leverage': data.get('leverage', 5),
            'start_date': data.get('start_date', '2024-06-15'),
            'end_date': data.get('end_date', '2024-07-15'),
            'bid_spread': data.get('bid_spread', 0.002),
            'ask_spread': data.get('ask_spread', 0.002)
        }

        logger.info(f"处理后的参数: {params}")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(params, f, ensure_ascii=False, indent=2)
            params_file = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            result_file = f.name

        try:
            # 调用独立回测执行器
            logger.info("启动独立回测进程...")
            result = subprocess.run([
                sys.executable, 
                str(BACKTEST_SCRIPT),
                "--params-file", params_file,
                "--output", result_file
            ], 
            capture_output=True, 
            text=True, 
            timeout=600,  # 10分钟超时
            cwd=str(PROJECT_ROOT),
            encoding='utf-8'
            )

            logger.info(f"回测进程返回码: {result.returncode}")

            if result.returncode == 0:
                # 读取结果文件
                with open(result_file, 'r', encoding='utf-8') as f:
                    backtest_result = json.load(f)

                logger.info("回测成功完成")
                return jsonify(backtest_result)
            else:
                error_msg = f'回测执行失败: {result.stderr}'
                logger.error(error_msg)
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 500

        finally:
            # 清理临时文件
            try:
                os.unlink(params_file)
                os.unlink(result_file)
            except:
                pass

    except subprocess.TimeoutExpired:
        error_msg = '回测执行超时'
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500
    except Exception as e:
        error_msg = f'服务器内部错误: {str(e)}'
        logger.error(f"API执行失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {e}")
    logger.error(traceback.format_exc())
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    # 检查依赖
    if not BACKTEST_SCRIPT.exists():
        logger.error(f"错误: 回测脚本不存在 {BACKTEST_SCRIPT}")
        sys.exit(1)
    
    logger.info("🚀 启动终极稳定后端服务...")
    logger.info(f"📍 服务地址: http://localhost:8000")
    logger.info(f"🔧 回测脚本: {BACKTEST_SCRIPT}")
    logger.info("🔄 服务器将持续运行，按 Ctrl+C 停止")
    
    try:
        app.run(
            host='0.0.0.0', 
            port=8000, 
            debug=False,  # 关闭debug避免重启
            threaded=True,  # 启用多线程
            use_reloader=False  # 关闭自动重载
        )
    except KeyboardInterrupt:
        logger.info("收到停止信号，服务器正在关闭...")
    except Exception as e:
        logger.error(f"服务器运行错误: {e}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("服务器已停止")

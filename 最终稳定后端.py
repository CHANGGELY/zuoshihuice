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

# 创建Flask应用
app = Flask(__name__)
CORS(app, origins=['http://localhost:5174'])  # 只允许前端域名

logger.info(f"🔍 项目根目录: {PROJECT_ROOT}")
logger.info(f"🔍 回测脚本: {BACKTEST_SCRIPT}")
logger.info(f"🔍 回测脚本存在: {BACKTEST_SCRIPT.exists()}")

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        return jsonify({
            'status': 'healthy',
            'backtest_script_exists': BACKTEST_SCRIPT.exists(),
            'project_root': str(PROJECT_ROOT)
        })
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

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

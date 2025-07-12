#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超稳定的后端服务
基于Flask，专门设计为持续运行不崩溃
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
import threading
import time
import signal
import atexit

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKTEST_SCRIPT = PROJECT_ROOT / "独立回测执行器.py"

print(f"🔍 项目根目录: {PROJECT_ROOT}")
print(f"🔍 回测脚本: {BACKTEST_SCRIPT}")
print(f"🔍 回测脚本存在: {BACKTEST_SCRIPT.exists()}")

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量用于控制服务器
server_running = True

def signal_handler(signum, frame):
    """信号处理器"""
    global server_running
    print(f"\n📡 收到信号 {signum}，准备优雅关闭...")
    server_running = False

def cleanup():
    """清理函数"""
    print("🧹 执行清理操作...")

# 注册信号处理器和清理函数
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
atexit.register(cleanup)

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        return jsonify({
            'status': 'ok',
            'backtest_script_exists': BACKTEST_SCRIPT.exists(),
            'project_root': str(PROJECT_ROOT),
            'server_running': server_running
        })
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/v1/backtest/run/', methods=['POST', 'OPTIONS'])
def run_backtest():
    """运行回测API"""
    if request.method == 'OPTIONS':
        # 处理预检请求
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        # 获取请求参数
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '缺少请求参数'
            }), 400

        print(f"📋 收到回测请求: {data}")

        # 验证回测脚本存在
        if not BACKTEST_SCRIPT.exists():
            return jsonify({
                'success': False,
                'error': f'回测脚本不存在: {BACKTEST_SCRIPT}'
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

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(params, f, ensure_ascii=False, indent=2)
            params_file = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            result_file = f.name

        try:
            # 调用独立回测执行器
            print("🚀 启动独立回测进程...")
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

            print(f"📊 回测进程返回码: {result.returncode}")

            if result.returncode == 0:
                # 读取结果文件
                with open(result_file, 'r', encoding='utf-8') as f:
                    backtest_result = json.load(f)

                print(f"✅ 回测成功完成")
                
                # 添加CORS头
                response = jsonify(backtest_result)
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            else:
                print(f"❌ 回测进程失败")
                print(f"❌ stderr: {result.stderr}")
                error_response = jsonify({
                    'success': False,
                    'error': f'回测执行失败: {result.stderr}'
                })
                error_response.headers.add('Access-Control-Allow-Origin', '*')
                return error_response, 500

        finally:
            # 清理临时文件
            try:
                os.unlink(params_file)
                os.unlink(result_file)
            except:
                pass

    except subprocess.TimeoutExpired:
        error_response = jsonify({
            'success': False,
            'error': '回测执行超时'
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500
    except Exception as e:
        print(f"❌ API执行失败: {e}")
        traceback.print_exc()
        error_response = jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

def run_server():
    """运行服务器"""
    print("🚀 启动超稳定后端服务...")
    print(f"📍 服务地址: http://localhost:8000")
    print(f"🔧 回测脚本: {BACKTEST_SCRIPT}")
    print("🔄 服务器将持续运行，按 Ctrl+C 停止")
    
    try:
        app.run(
            host='0.0.0.0', 
            port=8000, 
            debug=False,  # 关闭debug避免重启
            threaded=True,  # 启用多线程
            use_reloader=False  # 关闭自动重载
        )
    except KeyboardInterrupt:
        print("\n👋 收到停止信号，服务器正在关闭...")
    except Exception as e:
        print(f"❌ 服务器运行错误: {e}")
        traceback.print_exc()
    finally:
        global server_running
        server_running = False
        print("🛑 服务器已停止")

if __name__ == '__main__':
    # 检查依赖
    if not BACKTEST_SCRIPT.exists():
        print(f"❌ 错误: 回测脚本不存在 {BACKTEST_SCRIPT}")
        sys.exit(1)
    
    # 启动服务器
    try:
        run_server()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        traceback.print_exc()
        sys.exit(1)

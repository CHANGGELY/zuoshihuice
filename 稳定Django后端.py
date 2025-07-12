#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
稳定的Django后端服务
解决异步函数和全局状态冲突问题
"""

import os
import sys
import django
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import path
from django.core.wsgi import get_wsgi_application
import json
import subprocess
import tempfile
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()

# Django配置
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='your-secret-key-here',
        ALLOWED_HOSTS=['*'],
        ROOT_URLCONF=__name__,
        INSTALLED_APPS=[
            'corsheaders',
        ],
        MIDDLEWARE=[
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.common.CommonMiddleware',
        ],
        CORS_ALLOW_ALL_ORIGINS=True,
        CORS_ALLOW_CREDENTIALS=True,
        CORS_ALLOWED_HEADERS=[
            'accept',
            'accept-encoding',
            'authorization',
            'content-type',
            'dnt',
            'origin',
            'user-agent',
            'x-csrftoken',
            'x-requested-with',
        ],
    )

django.setup()

@csrf_exempt
@require_http_methods(["POST"])
def run_backtest(request):
    """运行回测API"""
    try:
        # 解析请求参数
        data = json.loads(request.body)
        print(f"📋 收到回测请求: {data}")
        
        # 创建参数文件
        params = {
            'strategy': data.get('strategy', 'grid_making'),
            'initial_capital': data.get('initial_capital', 10000),
            'leverage': data.get('leverage', 5),
            'start_date': data.get('start_date', '2024-06-15'),
            'end_date': data.get('end_date', '2024-07-15'),
            'bid_spread': data.get('bid_spread', 0.002),
            'ask_spread': data.get('ask_spread', 0.002)
        }
        
        # 创建临时参数文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(params, f, ensure_ascii=False, indent=2)
            params_file = f.name
        
        # 创建临时结果文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            result_file = f.name
        
        try:
            # 调用独立回测执行器
            print("🚀 启动独立回测进程...")
            result = subprocess.run([
                sys.executable, 
                str(PROJECT_ROOT / "独立回测执行器.py"),
                "--params-file", params_file,
                "--output", result_file
            ], 
            capture_output=True, 
            text=True, 
            timeout=300,  # 5分钟超时
            cwd=str(PROJECT_ROOT),
            encoding='utf-8'
            )
            
            print(f"📊 回测进程返回码: {result.returncode}")
            
            if result.returncode == 0:
                # 读取结果文件
                with open(result_file, 'r', encoding='utf-8') as f:
                    backtest_result = json.load(f)
                
                print(f"✅ 回测成功完成")
                return JsonResponse(backtest_result)
            else:
                print(f"❌ 回测进程失败")
                print(f"❌ stderr: {result.stderr}")
                return JsonResponse({
                    'success': False,
                    'error': f'回测执行失败: {result.stderr}'
                }, status=500)
                
        finally:
            # 清理临时文件
            try:
                os.unlink(params_file)
                os.unlink(result_file)
            except:
                pass
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON格式'
        }, status=400)
    except subprocess.TimeoutExpired:
        return JsonResponse({
            'success': False,
            'error': '回测执行超时'
        }, status=500)
    except Exception as e:
        print(f"❌ API执行失败: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """健康检查"""
    backtest_script = PROJECT_ROOT / "独立回测执行器.py"
    return JsonResponse({
        'status': 'ok',
        'backtest_script_exists': backtest_script.exists(),
        'project_root': str(PROJECT_ROOT)
    })

# URL配置
urlpatterns = [
    path('api/v1/backtest/run/', run_backtest, name='run_backtest'),
    path('api/v1/health/', health_check, name='health_check'),
]

# WSGI应用
application = get_wsgi_application()

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    import threading
    import time
    
    def run_server():
        """运行Django服务器"""
        print("🚀 启动稳定Django后端服务...")
        print(f"📍 服务地址: http://localhost:8000")
        print(f"🔧 项目根目录: {PROJECT_ROOT}")
        
        # 检查独立回测执行器
        backtest_script = PROJECT_ROOT / "独立回测执行器.py"
        print(f"🔧 回测脚本存在: {backtest_script.exists()}")
        
        execute_from_command_line([
            'manage.py', 'runserver', '8000', '--noreload'
        ])
    
    # 在单独线程中运行服务器
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(2)
    
    # 测试API
    try:
        import requests
        
        print("\n🧪 测试API...")
        
        # 健康检查
        health_response = requests.get('http://localhost:8000/api/v1/health/')
        print(f"健康检查: {health_response.status_code} - {health_response.json()}")
        
        # 回测API
        backtest_data = {
            'strategy': 'grid_making',
            'initial_capital': 10000,
            'leverage': 5,
            'start_date': '2024-06-15',
            'end_date': '2024-07-15'
        }
        
        print("开始回测测试...")
        backtest_response = requests.post(
            'http://localhost:8000/api/v1/backtest/run/',
            json=backtest_data,
            timeout=300
        )
        
        print(f"回测结果: {backtest_response.status_code}")
        if backtest_response.status_code == 200:
            result = backtest_response.json()
            if result.get('success'):
                data = result.get('data', {})
                print(f"✅ 回测成功!")
                print(f"📈 总收益率: {data.get('total_return', 0):.4f}")
                print(f"📊 交易次数: {data.get('total_trades', 0)}")
            else:
                print(f"❌ 回测失败: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {backtest_response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 保持服务器运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 服务器停止")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新回测服务器 - 修复版本
"""

import json
import subprocess
import tempfile
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewBacktestHandler(BaseHTTPRequestHandler):
    """新回测请求处理器"""
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """处理POST请求"""
        try:
            if self.path == '/api/v1/backtest/run':
                self.handle_backtest()
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"POST请求处理失败: {e}")
            self.send_error_response(f"服务器内部错误: {str(e)}")
    
    def do_GET(self):
        """处理GET请求"""
        try:
            if self.path == '/':
                response = {
                    "message": "新回测服务器",
                    "version": "2.0.0",
                    "status": "running"
                }
                self.send_json_response(response)
            elif self.path == '/health':
                response = {
                    "status": "healthy",
                    "message": "服务器运行正常"
                }
                self.send_json_response(response)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"GET请求处理失败: {e}")
            self.send_error_response(f"服务器内部错误: {str(e)}")
    
    def handle_backtest(self):
        """处理回测请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_response("请求体为空")
                return
                
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))
            
            logger.info(f"🚀 收到回测请求: {params}")
            
            # 验证参数
            required_fields = ['symbol', 'startDate', 'endDate', 'initialCapital', 'leverage']
            for field in required_fields:
                if field not in params:
                    self.send_error_response(f"缺少必需参数: {field}")
                    return
            
            # 创建临时参数文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(params, f, ensure_ascii=False, indent=2)
                params_file = f.name
            
            try:
                # 获取项目根目录
                project_root = Path(__file__).parent
                
                # 构建命令 - 使用进度回测执行器
                cmd = [
                    sys.executable, '-X', 'utf8',
                    str(project_root / "进度回测执行器.py"),
                    "--params-file", params_file
                ]
                
                logger.info(f"执行命令: {' '.join(cmd)}")
                
                # 执行子进程
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5分钟超时
                    cwd=str(project_root),
                    encoding='utf-8'
                )
                
                logger.info(f"子进程返回码: {result.returncode}")
                
                if result.returncode != 0:
                    logger.error(f"子进程错误: {result.stderr}")
                    self.send_error_response(f"回测执行失败: {result.stderr}")
                    return
                
                # 解析结果
                try:
                    backtest_result = json.loads(result.stdout)
                    
                    if "error" in backtest_result:
                        self.send_error_response(backtest_result["error"])
                        return
                    
                    # 发送成功响应
                    response = {
                        "success": True,
                        **backtest_result,  # 直接展开回测结果
                        "message": "回测完成"
                    }
                    self.send_json_response(response)
                    logger.info("✅ 回测成功完成")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
                    logger.error(f"原始输出: {result.stdout}")
                    self.send_error_response(f"结果解析失败: {e}")
                    
            finally:
                # 清理临时文件
                try:
                    Path(params_file).unlink()
                except:
                    pass
        
        except subprocess.TimeoutExpired:
            logger.error("回测超时")
            self.send_error_response("回测超时，请检查参数或减少回测时间范围")
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            self.send_error_response(f"请求参数格式错误: {e}")
        except Exception as e:
            logger.error(f"回测处理失败: {e}")
            self.send_error_response(f"回测处理失败: {str(e)}")
    
    def send_json_response(self, data):
        """发送JSON响应"""
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response_text = json.dumps(data, ensure_ascii=False, indent=2)
            self.wfile.write(response_text.encode('utf-8'))
        except Exception as e:
            logger.error(f"发送响应失败: {e}")
    
    def send_error_response(self, error_message):
        """发送错误响应"""
        try:
            response = {
                "success": False,
                "error": error_message,
                "message": "回测失败"
            }
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response_text = json.dumps(response, ensure_ascii=False, indent=2)
            self.wfile.write(response_text.encode('utf-8'))
        except Exception as e:
            logger.error(f"发送错误响应失败: {e}")
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    """启动服务器"""
    port = 8001
    
    try:
        server = HTTPServer(('localhost', port), NewBacktestHandler)
        
        print(f"🚀 新回测服务器启动成功!", flush=True)
        print(f"📊 服务地址: http://localhost:{port}", flush=True)
        print(f"🔗 健康检查: http://localhost:{port}/health", flush=True)
        print(f"📋 回测API: POST http://localhost:{port}/api/v1/backtest/run", flush=True)
        print("按 Ctrl+C 停止服务器", flush=True)
        print("-" * 50, flush=True)
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        if 'server' in locals():
            server.shutdown()
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        logger.error(f"服务器启动失败: {e}")

if __name__ == "__main__":
    main()

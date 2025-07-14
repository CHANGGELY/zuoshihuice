#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强回测服务器 - 支持K线图和交易标记
"""

import json
import subprocess
import tempfile
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedBacktestHandler(BaseHTTPRequestHandler):
    """增强回测请求处理器"""
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """处理POST请求"""
        if self.path == '/backtest':
            self.handle_backtest()
        else:
            self.send_error(404, "Not Found")
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/':
            response = {
                "message": "增强回测服务器",
                "version": "2.0.0",
                "status": "running"
            }
            self.send_json_response(response)
        elif self.path.startswith('/klines'):
            self.handle_klines()
        elif self.path == '/health':
            response = {
                "status": "healthy",
                "message": "服务器运行正常"
            }
            self.send_json_response(response)
        else:
            self.send_error(404, "Not Found")
    
    def handle_backtest(self):
        """处理回测请求"""
        try:
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))
            
            logger.info(f"收到回测请求: {params}")
            
            # 创建临时参数文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(params, f, ensure_ascii=False, indent=2)
                params_file = f.name
            
            try:
                # 执行独立回测执行器
                cmd = [
                    sys.executable, '-X', 'utf8',
                    str(Path(__file__).parent / "独立回测执行器.py"),
                    "--params-file", params_file
                ]
                
                logger.info(f"执行命令: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5分钟超时
                    cwd=str(Path(__file__).parent),
                    encoding='utf-8'
                )
                
                if result.returncode == 0:
                    # 解析输出
                    try:
                        response_data = json.loads(result.stdout)
                        logger.info("回测执行成功")
                        self.send_json_response(response_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"解析回测结果失败: {e}")
                        logger.error(f"原始输出: {result.stdout}")
                        self.send_error_response(f"解析回测结果失败: {str(e)}")
                else:
                    logger.error(f"回测执行失败，返回码: {result.returncode}")
                    logger.error(f"错误输出: {result.stderr}")
                    self.send_error_response(f"回测执行失败: {result.stderr}")
                    
            finally:
                # 清理临时文件
                try:
                    Path(params_file).unlink()
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"处理回测请求失败: {e}")
            self.send_error_response(f"处理回测请求失败: {str(e)}")
    
    def handle_klines(self):
        """处理K线数据请求"""
        try:
            # 解析查询参数
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            symbol = query_params.get('symbol', ['ETHUSDT'])[0]
            start_date = query_params.get('start_date', ['2025-05-15'])[0]
            end_date = query_params.get('end_date', ['2025-06-15'])[0]
            
            # 加载K线数据
            kline_data = self.load_kline_data(symbol, start_date, end_date)
            
            response = {
                "success": True,
                "data": kline_data,
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"获取K线数据失败: {e}")
            self.send_error_response(f"获取K线数据失败: {str(e)}")
    
    def load_kline_data(self, symbol, start_date, end_date):
        """加载K线数据"""
        import pandas as pd
        
        # 数据文件路径
        data_file = Path("K线data") / "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5"
        
        if not data_file.exists():
            raise FileNotFoundError(f"数据文件不存在: {data_file}")
        
        # 读取数据
        df = pd.read_hdf(data_file, key='klines')
        
        # 转换时间范围
        start_ts = int(pd.to_datetime(start_date).timestamp())
        end_ts = int(pd.to_datetime(end_date).timestamp())
        
        # 过滤数据
        mask = (df['timestamp'] >= start_ts) & (df['timestamp'] <= end_ts)
        filtered_df = df[mask].copy()
        
        # 转换为图表需要的格式
        kline_data = []
        for _, row in filtered_df.iterrows():
            kline_data.append({
                'timestamp': int(row['timestamp']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            })
        
        return kline_data
    
    def send_json_response(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def send_error_response(self, error_message):
        """发送错误响应"""
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {
            "success": False,
            "error": error_message,
            "message": "回测失败"
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    """启动服务器"""
    port = 8001  # 使用不同的端口避免冲突
    server = HTTPServer(('localhost', port), EnhancedBacktestHandler)

    print(f"🚀 增强回测服务器启动成功!", flush=True)
    print(f"📊 服务地址: http://localhost:{port}", flush=True)
    print(f"🔗 健康检查: http://localhost:{port}/health", flush=True)
    print(f"📋 回测API: POST http://localhost:{port}/backtest", flush=True)
    print(f"📈 K线API: GET http://localhost:{port}/klines", flush=True)
    print("按 Ctrl+C 停止服务器", flush=True)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        server.shutdown()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一回测服务器
集成K线数据加载和回测功能到一个端口
"""

import json
import sys
import subprocess
import tempfile
import os
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import pandas as pd
import numpy as np
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnifiedBacktestHandler(BaseHTTPRequestHandler):
    """统一回测处理器 - 集成K线数据和回测功能"""
    
    def __init__(self, *args, **kwargs):
        self.data_file = Path("K线data") / "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5"
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            if path == '/':
                self.handle_root_request()
            elif path == '/health':
                self.handle_health_request()
            elif path == '/klines':
                self.handle_klines_request(query_params)
            elif path == '/progress':
                self.handle_progress_request()
            else:
                self.send_error_response(404, "接口不存在")
                
        except Exception as e:
            logger.error(f"处理GET请求失败: {e}")
            self.send_error_response(500, str(e))
    
    def do_POST(self):
        """处理POST请求"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            if path == '/backtest' or path == '/api/v1/backtest/run':
                self.handle_backtest_request()
            else:
                self.send_error_response(404, "接口不存在")
                
        except Exception as e:
            logger.error(f"处理POST请求失败: {e}")
            self.send_error_response(500, str(e))
    
    def handle_root_request(self):
        """处理根路径请求"""
        response = {
            "message": "永续合约K线回测系统 - 统一服务器",
            "version": "3.0.0",
            "status": "running",
            "endpoints": {
                "klines": "GET /klines?symbol=ETHUSDT&start_date=2024-06-15&end_date=2024-07-15",
                "backtest": "POST /backtest",
                "progress": "GET /progress",
                "health": "GET /health"
            }
        }
        self.send_json_response(response)
    
    def handle_health_request(self):
        """处理健康检查请求"""
        response = {
            "status": "healthy",
            "message": "统一回测服务器运行正常",
            "data_file_exists": self.data_file.exists(),
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(response)
    
    def handle_klines_request(self, query_params):
        """处理K线数据请求"""
        try:
            # 获取参数
            symbol = query_params.get('symbol', ['ETHUSDT'])[0]
            start_date = query_params.get('start_date', [''])[0]
            end_date = query_params.get('end_date', [''])[0]
            timeframe = query_params.get('timeframe', ['1m'])[0]  # 🎯 新增时间周期参数

            if not start_date or not end_date:
                self.send_error_response(400, "缺少开始或结束日期参数")
                return

            logger.info(f"📊 加载K线数据: {symbol} {start_date} 到 {end_date} 周期: {timeframe}")
            
            # 检查数据文件
            if not self.data_file.exists():
                self.send_error_response(404, f"数据文件不存在: {self.data_file}")
                return
            
            # 加载数据
            df = pd.read_hdf(self.data_file, key='klines')
            
            # 过滤时间范围
            start_ts = int(pd.to_datetime(start_date).timestamp())
            end_ts = int(pd.to_datetime(end_date).timestamp())
            
            # 确保timestamp列是数值类型
            if df['timestamp'].dtype == 'datetime64[ns]':
                df['timestamp'] = df['timestamp'].astype('int64') // 10**9
            
            mask = (df['timestamp'] >= start_ts) & (df['timestamp'] <= end_ts)
            filtered_df = df[mask].copy()
            
            if len(filtered_df) == 0:
                self.send_error_response(400, f"指定时间范围内没有数据: {start_date} 到 {end_date}")
                return

            # 🎯 时间周期重采样
            if timeframe != '1m':
                filtered_df = self.resample_klines(filtered_df, timeframe)

            # 转换为前端需要的格式
            klines = []
            for _, row in filtered_df.iterrows():
                # 计算成交额 (如果没有quote_volume字段)
                quote_volume = row.get('quote_volume', row['volume'] * row['close'])

                klines.append({
                    'timestamp': int(row['timestamp']),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume']),
                    'quote_volume': float(quote_volume)  # 确保包含成交额字段
                })
            
            response_data = {
                'success': True,
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date,
                'count': len(klines),
                'klines': klines
            }
            
            self.send_json_response(response_data)
            logger.info(f"✅ 成功返回 {len(klines)} 条K线数据")
            
        except Exception as e:
            logger.error(f"处理K线数据请求失败: {e}")
            self.send_error_response(500, str(e))

    def resample_klines(self, df, timeframe):
        """🎯 K线数据重采样"""
        try:
            # 设置时间索引
            df_copy = df.copy()
            df_copy['datetime'] = pd.to_datetime(df_copy['timestamp'], unit='s')
            df_copy.set_index('datetime', inplace=True)

            # 定义重采样规则 (修复弃用警告)
            resample_rules = {
                '1h': '1h',    # 1小时 (修复: 使用小写h)
                '1d': '1D',    # 1天
                '1M': '1M'     # 1月
            }

            if timeframe not in resample_rules:
                logger.warning(f"不支持的时间周期: {timeframe}，使用原始1分钟数据")
                return df

            rule = resample_rules[timeframe]

            # 执行重采样 (修复: 移除不存在的quote_volume列)
            resampled = df_copy.resample(rule).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()

            # 重新计算timestamp
            resampled['timestamp'] = resampled.index.astype('int64') // 10**9
            resampled.reset_index(drop=True, inplace=True)

            logger.info(f"重采样完成: {len(df)} -> {len(resampled)} 条数据 ({timeframe})")
            return resampled

        except Exception as e:
            logger.error(f"重采样失败: {e}")
            return df  # 返回原始数据

    def handle_progress_request(self):
        """处理进度查询请求"""
        try:
            # 读取进度文件
            progress_file = Path("progress.json")
            if progress_file.exists():
                with open(progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
            else:
                progress_data = {'progress': 0, 'message': '等待中...'}
            
            self.send_json_response(progress_data)
            
        except Exception as e:
            logger.error(f"处理进度请求失败: {e}")
            self.send_error_response(500, str(e))
    
    def handle_backtest_request(self):
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
                    # 智能提取JSON - 处理多行JSON对象
                    stdout_text = result.stdout.strip()

                    # 方法1: 查找完整的JSON对象（支持多行）
                    brace_count = 0
                    json_start = -1
                    json_end = -1

                    for i, char in enumerate(stdout_text):
                        if char == '{':
                            if brace_count == 0:
                                json_start = i
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0 and json_start != -1:
                                json_end = i
                                # 检查是否包含success字段
                                potential_json = stdout_text[json_start:json_end + 1]
                                if '"success"' in potential_json:
                                    break

                    if json_start != -1 and json_end != -1:
                        json_line = stdout_text[json_start:json_end + 1]
                    else:
                        # 方法2: 按行查找
                        stdout_lines = stdout_text.split('\n')
                        json_lines = []
                        in_json = False

                        for line in stdout_lines:
                            line = line.strip()
                            if line.startswith('{') and '"success"' in line:
                                json_lines = [line]
                                in_json = True
                            elif in_json:
                                json_lines.append(line)
                                if line.endswith('}') and line.count('}') >= line.count('{'):
                                    break

                        if json_lines:
                            json_line = '\n'.join(json_lines)
                        else:
                            json_line = stdout_text
                    
                    # 清理JSON字符串，移除可能的额外数据
                    json_line = json_line.strip()

                    # 如果JSON后面有额外数据，截取到第一个完整的JSON对象
                    decoder = json.JSONDecoder()
                    try:
                        backtest_result, idx = decoder.raw_decode(json_line)
                    except json.JSONDecodeError:
                        # 备用方案：尝试直接解析
                        backtest_result = json.loads(json_line)
                    
                    if "error" in backtest_result:
                        self.send_error_response(backtest_result["error"])
                        return
                    
                    # 🚀 用户要求显示所有交易标记，移除限制
                    # 前端通过开关功能控制显示哪些交易类型，提供更好的用户体验
                    if "trades" in backtest_result:
                        total_trades = len(backtest_result["trades"])
                        backtest_result["trades_truncated"] = False
                        backtest_result["total_trades_original"] = total_trades
                        backtest_result["total_trades_shown"] = total_trades
                        logger.info(f"返回所有交易记录: {total_trades} 个")
                    
                    # 构建响应
                    response = {
                        "success": True,
                        **backtest_result,
                        "message": "回测完成"
                    }
                    
                    self.send_json_response(response)
                    logger.info("✅ 回测成功完成")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
                    logger.error(f"原始输出前1000字符: {result.stdout[:1000]}")
                    self.send_error_response(f"回测结果解析失败: {str(e)}")
                    
            finally:
                # 清理临时文件
                try:
                    Path(params_file).unlink()
                except:
                    pass
                    
        except json.JSONDecodeError as e:
            logger.error(f"请求参数解析失败: {e}")
            self.send_error_response(f"请求参数格式错误: {e}")
        except Exception as e:
            logger.error(f"回测处理失败: {e}")
            self.send_error_response(f"回测处理失败: {str(e)}")
    
    def send_cors_headers(self):
        """发送CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def send_json_response(self, data):
        """发送JSON响应"""
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_cors_headers()
            self.end_headers()
            
            # 使用更安全的JSON序列化
            response_text = json.dumps(data, ensure_ascii=False, indent=2, default=str)
            self.wfile.write(response_text.encode('utf-8'))
            logger.info("✅ JSON响应发送成功")
            
        except Exception as e:
            logger.error(f"发送响应失败: {e}")
            # 尝试发送简化的错误响应
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_cors_headers()
                self.end_headers()
                error_response = {"success": False, "error": f"响应序列化失败: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
            except:
                pass
    
    def send_error_response(self, message):
        """发送错误响应"""
        try:
            error_data = {
                'success': False,
                'error': message,
                'timestamp': datetime.now().isoformat()
            }
            
            response_json = json.dumps(error_data, ensure_ascii=False, indent=2)
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_cors_headers()
            self.end_headers()
            
            self.wfile.write(response_json.encode('utf-8'))
            logger.error(f"❌ 错误响应: {message}")
            
        except Exception as e:
            logger.error(f"发送错误响应失败: {e}")
    
    def log_message(self, format, *args):
        """重写日志方法，使用标准日志"""
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    """主函数"""
    # 检查数据文件
    data_file = Path("K线data") / "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5"
    if not data_file.exists():
        print(f"❌ 数据文件不存在: {data_file}")
        print("请确保数据文件存在后再启动服务器")
        return
    
    # 启动统一服务器
    port = 8001
    server = HTTPServer(('localhost', port), UnifiedBacktestHandler)
    
    print("=" * 60)
    print("🚀 永续合约K线回测系统 - 统一服务器启动成功!")
    print("=" * 60)
    print(f"📊 服务地址: http://localhost:{port}")
    print(f"🔗 健康检查: http://localhost:{port}/health")
    print(f"📈 K线数据: GET http://localhost:{port}/klines")
    print(f"🔥 回测接口: POST http://localhost:{port}/backtest")
    print(f"⏳ 进度查询: GET http://localhost:{port}/progress")
    print(f"📁 数据文件: {data_file}")
    print("=" * 60)
    print("按 Ctrl+C 停止服务器")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        server.shutdown()

if __name__ == "__main__":
    main()

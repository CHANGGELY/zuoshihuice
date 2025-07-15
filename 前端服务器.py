#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端服务器
提供完整的Web前端界面
"""

import json
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrontendHandler(BaseHTTPRequestHandler):
    """前端处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            if path == '/' or path == '/index.html':
                self.serve_main_page()
            elif path == '/api/test':
                self.serve_api_test()
            else:
                self.send_error(404, "页面不存在")
                
        except Exception as e:
            logger.error(f"处理GET请求失败: {e}")
            self.send_error(500, str(e))
    
    def serve_main_page(self):
        """提供主页面"""
        html_content = self.get_main_html()
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        self.wfile.write(html_content.encode('utf-8'))
    
    def serve_api_test(self):
        """API测试接口"""
        response = {
            "status": "success",
            "message": "前端服务器运行正常",
            "backend_url": "http://localhost:8001"
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def get_main_html(self):
        """获取主页面HTML"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>永续合约K线回测系统 - Web版</title>
    <!-- 轻量级图表库 -->
    <script src="https://cdn.jsdelivr.net/npm/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
    <!-- Chart.js for 资金曲线 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .content {
            padding: 20px;
        }
        
        .controls-panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 5px solid #667eea;
        }
        
        .controls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group label {
            font-weight: bold;
            margin-bottom: 5px;
            color: #555;
        }
        
        .form-group input, .form-group select {
            padding: 8px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }

        /* 交易标记开关样式 */
        .checkbox-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }

        .checkbox-label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            cursor: pointer;
            padding: 8px;
            border-radius: 6px;
            transition: background-color 0.2s;
        }

        .checkbox-label:hover {
            background-color: rgba(102, 126, 234, 0.1);
        }

        .checkbox-label input[type="checkbox"] {
            margin: 0;
            width: 16px;
            height: 16px;
        }

        .marker-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            border: 1px solid #ccc;
        }

        .form-section {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .form-section h4 {
            margin: 0 0 10px 0;
            color: #333;
            font-size: 16px;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .charts-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .chart-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
            margin-bottom: 10px;
        }

        .kline-container {
            min-height: 520px;
        }

        .equity-container {
            min-height: 270px;
        }
        
        .chart-header {
            background: #f8f9fa;
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chart-header h3 {
            color: #333;
            margin: 0;
        }

        /* 🎯 时间周期选择器样式 */
        .timeframe-selector {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .timeframe-selector select {
            background: #2b2b2b;
            color: #f0b90b;
            border: 1px solid #f0b90b;
            border-radius: 4px;
            padding: 5px 10px;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            outline: none;
        }

        .timeframe-selector select:hover {
            background: #3b3b3b;
        }

        .timeframe-selector select:focus {
            box-shadow: 0 0 5px rgba(240, 185, 11, 0.5);
        }
        
        .chart-info {
            font-size: 12px;
            color: #666;
        }
        
        #klineChart {
            width: 100%;
            height: 500px;
        }

        #equityChart {
            width: 100%;
            height: 250px;
        }
        
        .progress-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: none;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s;
        }
        
        .progress-text {
            text-align: center;
            font-weight: bold;
            color: #333;
        }
        
        .status {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .hidden {
            display: none !important;
        }
        
        .results-panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .metric-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }
        
        .metric-value.positive {
            color: #28a745;
        }
        
        .metric-value.negative {
            color: #dc3545;
        }
        
        .server-status {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
        }
        
        .server-status.online {
            background: rgba(40, 167, 69, 0.9);
        }
        
        .server-status.offline {
            background: rgba(220, 53, 69, 0.9);
        }
    </style>
</head>
<body>
    <div class="server-status" id="serverStatus">🔄 检查服务器状态...</div>
    
    <div class="container">
        <div class="header">
            <h1>📊 永续合约K线回测系统</h1>
            <p>专业Web版量化交易回测平台 | 前端端口: 3000 | 后端端口: 8001</p>
        </div>
        
        <div class="content">
            <!-- 控制面板 -->
            <div class="controls-panel">
                <h3>🎛️ 控制面板</h3>
                <div class="controls-grid">
                    <div class="form-group">
                        <label>交易对</label>
                        <select id="symbol">
                            <option value="ETHUSDT">ETHUSDT</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>开始日期</label>
                        <input type="date" id="startDate" value="2025-05-15" min="2019-11-01" max="2025-06-15">
                    </div>
                    <div class="form-group">
                        <label>结束日期</label>
                        <input type="date" id="endDate" value="2025-06-15" min="2019-11-01" max="2025-06-15">
                    </div>
                    <div class="form-group">
                        <label>初始资金 (USDT)</label>
                        <input type="number" id="initialCapital" value="600" step="0.01">
                    </div>
                    <div class="form-group">
                        <label>杠杆倍数</label>
                        <input type="number" id="leverage" value="125" min="1" max="125">
                    </div>
                    <div class="form-group">
                        <label>买单价差</label>
                        <input type="number" id="bidSpread" value="0.002" step="0.0001" title="买单价差比例">
                    </div>
                    <div class="form-group">
                        <label>卖单价差</label>
                        <input type="number" id="askSpread" value="0.002" step="0.0001" title="卖单价差比例">
                    </div>
                    <div class="form-group">
                        <label>仓位比例</label>
                        <input type="number" id="positionSizeRatio" value="0.02" step="0.001" title="每次下单占总权益的比例">
                    </div>
                    <div class="form-group">
                        <label>最大仓位比例</label>
                        <input type="number" id="maxPositionRatio" value="0.8" step="0.01" title="最大仓位价值不超过权益的比例">
                    </div>
                    <div class="form-group">
                        <label>订单刷新时间(秒)</label>
                        <input type="number" id="orderRefreshTime" value="30" step="1" title="订单刷新间隔">
                    </div>
                    <div class="form-group">
                        <label>启用动态下单量</label>
                        <input type="checkbox" id="useDynamicOrderSize" checked title="是否使用动态下单量">
                    </div>
                    <div class="form-group">
                        <label>Maker手续费率</label>
                        <input type="number" id="makerFee" value="0.0002" step="0.0001" title="Maker订单手续费率">
                    </div>
                    <div class="form-group">
                        <label>Taker手续费率</label>
                        <input type="number" id="takerFee" value="0.0005" step="0.0001" title="Taker订单手续费率">
                    </div>
                    <div class="form-group">
                        <label>启用返佣</label>
                        <input type="checkbox" id="useFeeRebate" checked title="是否启用手续费返佣">
                    </div>
                    <div class="form-group">
                        <label>返佣比例</label>
                        <input type="number" id="rebateRate" value="0.30" step="0.01" min="0" max="1" title="手续费返佣比例 (0-1)">
                    </div>
                </div>

                <!-- 交易标记开关 -->
                <div class="form-section">
                    <h4>🎯 交易标记显示</h4>
                    <div class="checkbox-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="showBuyLong" checked>
                            <span class="marker-color" style="background-color: #00ff00;"></span>
                            开多标记
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="showSellShort" checked>
                            <span class="marker-color" style="background-color: #ff0000;"></span>
                            开空标记
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="showSellLong" checked>
                            <span class="marker-color" style="background-color: #ffaa00;"></span>
                            平多标记
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="showBuyShort" checked>
                            <span class="marker-color" style="background-color: #00aaff;"></span>
                            平空标记
                        </label>
                    </div>
                </div>
                
                <div class="button-group">
                    <button class="btn btn-primary" onclick="loadKlineData()">📊 加载K线数据</button>
                    <button class="btn btn-primary" onclick="runBacktest()" id="backtestBtn">🚀 开始回测</button>
                    <button class="btn btn-secondary" onclick="clearCharts()">🗑️ 清空图表</button>
                </div>
            </div>
            
            <!-- 进度显示 -->
            <div class="progress-container" id="progressContainer">
                <h3>⏳ 回测进度</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="progress-text" id="progressText">准备中...</div>
                <div class="status hidden" id="status"></div>
            </div>
            
            <!-- 图表容器 -->
            <div class="charts-container">
                <!-- K线图表 -->
                <div class="chart-container kline-container">
                    <div class="chart-header">
                        <h3>📈 K线图表</h3>
                        <!-- 🎯 时间周期选择器 - 移到图表内部 -->
                        <div class="timeframe-selector">
                            <select id="timeframe">
                                <option value="1m" selected>1分钟</option>
                                <option value="1h">1小时</option>
                                <option value="1d">1天</option>
                                <option value="1M">1月</option>
                            </select>
                        </div>
                        <div class="chart-info" id="klineInfo">
                            数据范围: 2019-11-01 至 2025-06-15 | 请选择时间范围加载数据
                        </div>
                        <!-- 🎯 K线悬停信息显示 -->
                        <div id="klineTooltip" style="display: none; position: absolute; background: rgba(0,0,0,0.8); color: white; padding: 10px; border-radius: 5px; font-size: 12px; z-index: 1000; pointer-events: none;">
                            <div id="tooltipContent"></div>
                        </div>
                    </div>
                    <div id="klineChart" style="position: relative;"></div>
                </div>

                <!-- 资金曲线图 -->
                <div class="chart-container equity-container">
                    <div class="chart-header">
                        <h3>💰 资金曲线</h3>
                        <div class="chart-info" id="equityInfo">
                            等待回测数据...
                        </div>
                    </div>
                    <div id="equityChart"></div>
                </div>
            </div>
            
            <!-- 回测结果 -->
            <div class="results-panel hidden" id="resultsPanel">
                <h3>📊 回测结果</h3>
                <div class="metrics-grid" id="metricsGrid">
                    <!-- 动态生成指标卡片 -->
                </div>
            </div>
        </div>
    </div>

    <script>
        let klineChart = null;
        let candlestickSeries = null;
        let equityChart = null;
        let equityLineSeries = null;
        let currentKlineData = null;
        let progressInterval = null;
        let tradeMarkers = []; // 存储交易标记
        const BACKEND_URL = 'http://localhost:8001';
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            // 设置正确的日期范围（数据范围：2019-11-01 至 2025-06-15）
            // 默认使用最近一个月的数据
            document.getElementById('endDate').value = '2025-06-15';  // 数据截止日期
            document.getElementById('startDate').value = '2025-05-15'; // 最近一个月

            // 检查服务器状态
            checkServerStatus();
            setInterval(checkServerStatus, 30000); // 每30秒检查一次

            // 添加交易标记开关事件监听器
            ['showBuyLong', 'showSellShort', 'showSellLong', 'showBuyShort'].forEach(id => {
                document.getElementById(id).addEventListener('change', updateTradeMarkers);
            });

            // 🎯 添加时间周期选择器事件监听器
            document.getElementById('timeframe').addEventListener('change', function() {
                const timeframe = this.value;
                console.log(`时间周期切换到: ${timeframe}`);

                // 如果已经加载了K线数据，重新加载
                const startDate = document.getElementById('startDate').value;
                const endDate = document.getElementById('endDate').value;

                if (startDate && endDate) {
                    loadKlineData(startDate, endDate, timeframe);
                }
            });
        });
        
        // 检查服务器状态
        async function checkServerStatus() {
            const statusElement = document.getElementById('serverStatus');
            try {
                const response = await fetch(`${BACKEND_URL}/health`);
                if (response.ok) {
                    statusElement.textContent = '🟢 后端服务器在线';
                    statusElement.className = 'server-status online';
                } else {
                    throw new Error('服务器响应异常');
                }
            } catch (error) {
                statusElement.textContent = '🔴 后端服务器离线';
                statusElement.className = 'server-status offline';
            }
        }

        // 加载K线数据
        async function loadKlineData(customStartDate = null, customEndDate = null, customTimeframe = null) {
            try {
                const symbol = document.getElementById('symbol').value;
                const startDate = customStartDate || document.getElementById('startDate').value;
                const endDate = customEndDate || document.getElementById('endDate').value;
                const timeframe = customTimeframe || document.getElementById('timeframe').value;

                if (!startDate || !endDate) {
                    alert('请选择开始和结束日期');
                    return;
                }

                // 更新图表信息
                const timeframeText = {
                    '1m': '1分钟',
                    '1h': '1小时',
                    '1d': '1天',
                    '1M': '1月'
                }[timeframe] || timeframe;
                document.getElementById('klineInfo').textContent = `正在加载 ${symbol} ${startDate} 至 ${endDate} 的${timeframeText}K线数据...`;

                // 请求K线数据
                const response = await fetch(`${BACKEND_URL}/klines?symbol=${symbol}&start_date=${startDate}&end_date=${endDate}&timeframe=${timeframe}`);
                const data = await response.json();

                if (!data.success) {
                    throw new Error(data.error || '获取K线数据失败');
                }

                currentKlineData = data;
                displayKlineChart(data);

                // 更新图表信息
                const sourceText = data.source === 'cache' ? '⚡缓存' : '🔄实时';
                document.getElementById('klineInfo').textContent =
                    `${symbol} | ${startDate} 至 ${endDate} | ${timeframeText} | 共 ${data.klines.length} 条K线数据 | ${sourceText}`;

            } catch (error) {
                console.error('加载K线数据失败:', error);
                alert(`加载K线数据失败: ${error.message}`);
                document.getElementById('klineInfo').textContent = '数据加载失败';
            }
        }

        // 显示K线图表
        function displayKlineChart(data) {
            try {
                const chartContainer = document.getElementById('klineChart');
                chartContainer.innerHTML = ''; // 清空容器

                // 创建轻量级图表 - 币安风格
                klineChart = LightweightCharts.createChart(chartContainer, {
                    width: chartContainer.clientWidth,
                    height: 600,
                    layout: {
                        backgroundColor: '#1e1e1e',  // 深色背景
                        textColor: '#d1d4dc',       // 浅色文字
                    },
                    grid: {
                        vertLines: {
                            color: '#2a2a2a',
                            style: 1,
                        },
                        horzLines: {
                            color: '#2a2a2a',
                            style: 1,
                        },
                    },
                    crosshair: {
                        mode: LightweightCharts.CrosshairMode.Normal,
                        vertLine: {
                            color: '#758696',
                            width: 1,
                            style: 3, // 虚线
                            labelBackgroundColor: '#4c525e',
                        },
                        horzLine: {
                            color: '#758696',
                            width: 1,
                            style: 3, // 虚线
                            labelBackgroundColor: '#4c525e',
                        },
                    },
                    rightPriceScale: {
                        borderColor: '#485158',
                        textColor: '#d1d4dc',
                    },
                    timeScale: {
                        borderColor: '#485158',
                        textColor: '#d1d4dc',
                        timeVisible: true,
                        secondsVisible: false,
                    },
                });

                // 添加K线数据 - 币安风格颜色
                candlestickSeries = klineChart.addCandlestickSeries({
                    upColor: '#0ecb81',      // 绿色（涨）
                    downColor: '#f6465d',    // 红色（跌）
                    borderVisible: false,
                    wickUpColor: '#0ecb81',
                    wickDownColor: '#f6465d',
                });

                // 转换数据格式
                const klineData = data.klines.map(kline => ({
                    time: kline.timestamp,
                    open: kline.open,
                    high: kline.high,
                    low: kline.low,
                    close: kline.close,
                }));

                candlestickSeries.setData(klineData);

                // 🎯 添加鼠标悬停信息显示
                setupKlineCrosshairHandler(klineChart, candlestickSeries, data.klines);

                // 自适应大小
                window.addEventListener('resize', () => {
                    klineChart.applyOptions({ width: chartContainer.clientWidth });
                });

                console.log(`K线图表已加载，共 ${klineData.length} 条数据`);

            } catch (error) {
                console.error('显示K线图失败:', error);
                document.getElementById('klineChart').innerHTML =
                    `<p style="text-align: center; color: #dc3545; padding: 50px;">K线图加载失败: ${error.message}</p>`;
            }
        }

        // 显示资金曲线图
        function displayEquityChart(equityHistory) {
            try {
                const chartContainer = document.getElementById('equityChart');

                // 销毁现有图表
                if (equityChart) {
                    equityChart.remove();
                    equityChart = null;
                    equityLineSeries = null;
                }

                // 创建LightweightCharts图表
                equityChart = LightweightCharts.createChart(chartContainer, {
                    width: chartContainer.clientWidth,
                    height: 250,
                    layout: {
                        backgroundColor: '#ffffff',
                        textColor: '#333',
                    },
                    grid: {
                        vertLines: {
                            color: '#e1e1e1',
                        },
                        horzLines: {
                            color: '#e1e1e1',
                        },
                    },
                    crosshair: {
                        mode: LightweightCharts.CrosshairMode.Normal,
                    },
                    rightPriceScale: {
                        borderColor: '#cccccc',
                        scaleMargins: {
                            top: 0.1,
                            bottom: 0.1,
                        },
                    },
                    timeScale: {
                        borderColor: '#cccccc',
                        timeVisible: true,
                        secondsVisible: false,
                    },
                    localization: {
                        priceFormatter: (price) => `${price.toFixed(2)} USDT`,
                        timeFormatter: (time) => {
                            const date = new Date(time * 1000);
                            return date.toLocaleString('zh-CN', {
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                            });
                        },
                    },
                });

                // 创建线条系列
                equityLineSeries = equityChart.addLineSeries({
                    color: '#667eea',
                    lineWidth: 3,
                    crosshairMarkerVisible: true,
                    crosshairMarkerRadius: 6,
                    crosshairMarkerBorderColor: '#667eea',
                    crosshairMarkerBackgroundColor: '#667eea',
                    lastValueVisible: true,
                    priceLineVisible: true,
                    title: '账户权益',
                });

                // 准备数据 - 转换为LightweightCharts格式
                const equityData = equityHistory.map(point => ({
                    time: point[0], // 时间戳
                    value: point[1]  // 权益值
                }));

                // 设置数据
                equityLineSeries.setData(equityData);

                // 自适应大小
                window.addEventListener('resize', () => {
                    equityChart.applyOptions({ width: chartContainer.clientWidth });
                });

                // 更新图表信息
                const initialEquity = equityHistory[0][1];
                const finalEquity = equityHistory[equityHistory.length - 1][1];
                const totalReturn = ((finalEquity - initialEquity) / initialEquity * 100).toFixed(2);

                document.getElementById('equityInfo').textContent =
                    `初始: ${initialEquity.toFixed(2)} USDT | 最终: ${finalEquity.toFixed(2)} USDT | 收益: ${totalReturn}%`;

                console.log(`资金曲线图已加载，共 ${equityHistory.length} 个数据点`);

            } catch (error) {
                console.error('显示资金曲线图失败:', error);
                document.getElementById('equityInfo').textContent = '资金曲线图加载失败';
                document.getElementById('equityChart').innerHTML =
                    `<p style="text-align: center; color: #dc3545; padding: 50px;">资金曲线图加载失败: ${error.message}</p>`;
            }
        }

        // 在K线图上显示交易标记
        function displayTradeMarkers(trades) {
            if (!candlestickSeries || !trades || trades.length === 0) {
                console.log('无法显示交易标记：缺少K线图或交易数据');
                return;
            }

            try {
                // 清除现有标记
                tradeMarkers = [];

                // 获取开关状态
                const showBuyLong = document.getElementById('showBuyLong').checked;
                const showSellShort = document.getElementById('showSellShort').checked;
                const showSellLong = document.getElementById('showSellLong').checked;
                const showBuyShort = document.getElementById('showBuyShort').checked;

                // 为每个交易创建标记
                const markers = trades.filter(trade => {
                    const side = trade.side.toUpperCase();
                    // 根据开关状态过滤交易
                    switch(side) {
                        case 'BUY_LONG': return showBuyLong;
                        case 'SELL_SHORT': return showSellShort;
                        case 'SELL_LONG': return showSellLong;
                        case 'BUY_SHORT': return showBuyShort;
                        default: return false;
                    }
                }).map(trade => {
                    const timestamp = trade.timestamp;
                    const side = trade.side.toUpperCase();

                    // 根据交易类型设置标记样式
                    let color, shape, text, position;

                    switch(side) {
                        case 'BUY_LONG':  // 买入开多
                            color = '#00ff00';  // 绿色
                            shape = 'arrowUp';
                            text = '开多';
                            position = 'belowBar';
                            break;
                        case 'SELL_SHORT':  // 卖出开空
                            color = '#ff0000';  // 红色
                            shape = 'arrowDown';
                            text = '开空';
                            position = 'aboveBar';
                            break;
                        case 'SELL_LONG':  // 卖出平多
                            color = '#ffaa00';  // 橙色
                            shape = 'arrowDown';
                            text = '平多';
                            position = 'aboveBar';
                            break;
                        case 'BUY_SHORT':  // 买入平空
                            color = '#00aaff';  // 蓝色
                            shape = 'arrowUp';
                            text = '平空';
                            position = 'belowBar';
                            break;
                        default:
                            color = '#888888';
                            shape = 'circle';
                            text = '交易';
                            position = 'belowBar';
                    }

                    return {
                        time: timestamp,
                        position: position,
                        color: color,
                        shape: shape,
                        text: `${text}\n${trade.price.toFixed(2)}`,
                        size: 1.5
                    };
                });

                // 设置标记到K线图
                candlestickSeries.setMarkers(markers);
                tradeMarkers = markers;

                console.log(`已在K线图上显示 ${markers.length} 个交易标记 (总交易数: ${trades.length})`);

            } catch (error) {
                console.error('显示交易标记失败:', error);
            }
        }

        // 更新交易标记显示（当开关状态改变时调用）
        function updateTradeMarkers() {
            if (window.currentBacktestResult && window.currentBacktestResult.trades) {
                displayTradeMarkers(window.currentBacktestResult.trades);
            }
        }

        // 🎯 设置K线图悬停信息处理
        function setupKlineCrosshairHandler(chart, series, klineData) {
            const tooltip = document.getElementById('klineTooltip');
            const tooltipContent = document.getElementById('tooltipContent');

            chart.subscribeCrosshairMove(param => {
                if (param.point === undefined || !param.time || param.point.x < 0 || param.point.y < 0) {
                    tooltip.style.display = 'none';
                    return;
                }

                // 查找对应的K线数据
                const klineIndex = klineData.findIndex(k => k.timestamp === param.time);
                if (klineIndex === -1) {
                    tooltip.style.display = 'none';
                    return;
                }

                const kline = klineData[klineIndex];

                // 计算涨跌幅和振幅
                const prevClose = klineIndex > 0 ? klineData[klineIndex - 1].close : kline.open;
                const change = kline.close - prevClose;
                const changePercent = ((change / prevClose) * 100).toFixed(2);
                const amplitude = (((kline.high - kline.low) / prevClose) * 100).toFixed(2);

                // 计算VWAP (成交额/成交量) - 处理没有quote_volume的情况
                const quoteVolume = kline.quote_volume || (kline.volume * kline.close); // 如果没有成交额，用成交量*收盘价估算
                const vwap = kline.volume > 0 ? (quoteVolume / kline.volume).toFixed(4) : '0.0000';

                // 格式化时间
                const date = new Date(param.time * 1000);
                const timeStr = date.toLocaleString('zh-CN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });

                // 构建悬停信息内容
                const changeColor = change >= 0 ? '#0ecb81' : '#f6465d';
                tooltipContent.innerHTML = `
                    <div style="margin-bottom: 5px; font-weight: bold;">${timeStr}</div>
                    <div>开盘: <span style="color: #d1d4dc;">${kline.open.toFixed(4)}</span></div>
                    <div>最高: <span style="color: #d1d4dc;">${kline.high.toFixed(4)}</span></div>
                    <div>最低: <span style="color: #d1d4dc;">${kline.low.toFixed(4)}</span></div>
                    <div>收盘: <span style="color: #d1d4dc;">${kline.close.toFixed(4)}</span></div>
                    <div>涨跌幅: <span style="color: ${changeColor};">${changePercent}%</span></div>
                    <div>振幅: <span style="color: #d1d4dc;">${amplitude}%</span></div>
                    <div>成交量: <span style="color: #d1d4dc;">${kline.volume.toFixed(2)}</span></div>
                    <div>成交额: <span style="color: #d1d4dc;">${quoteVolume.toFixed(2)}</span></div>
                    <div>VWAP: <span style="color: #d1d4dc;">${vwap}</span></div>
                `;

                // 定位悬停框
                const chartRect = chart.chartElement().getBoundingClientRect();
                tooltip.style.display = 'block';
                tooltip.style.left = (param.point.x + 15) + 'px';
                tooltip.style.top = (param.point.y - 10) + 'px';
            });
        }

        // 清空图表
        function clearCharts() {
            if (klineChart) {
                klineChart.remove();
                klineChart = null;
                candlestickSeries = null;
            }

            if (equityChart) {
                equityChart.remove();
                equityChart = null;
                equityLineSeries = null;
            }

            currentKlineData = null;
            tradeMarkers = []; // 清空交易标记
            document.getElementById('klineInfo').textContent = '数据范围: 2019-11-01 至 2025-06-15 | 请选择时间范围加载数据';
            document.getElementById('equityInfo').textContent = '等待回测数据...';
            document.getElementById('resultsPanel').classList.add('hidden');
        }

        // 运行回测
        async function runBacktest() {
            if (!currentKlineData) {
                alert('请先加载K线数据');
                return;
            }

            const button = document.getElementById('backtestBtn');
            const progressContainer = document.getElementById('progressContainer');
            const status = document.getElementById('status');

            try {
                // 禁用按钮
                button.disabled = true;
                button.textContent = '⏳ 回测中...';

                // 显示进度
                progressContainer.classList.remove('hidden');
                status.classList.add('hidden');
                updateProgress(0, "准备回测参数...");

                // 收集参数 - 与backtest_kline_trajectory.py保持一致
                const params = {
                    symbol: document.getElementById('symbol').value,
                    startDate: document.getElementById('startDate').value,
                    endDate: document.getElementById('endDate').value,
                    initialCapital: parseFloat(document.getElementById('initialCapital').value),
                    leverage: parseInt(document.getElementById('leverage').value),

                    // 🎯 新增参数，与backtest_kline_trajectory.py一致
                    bidSpread: parseFloat(document.getElementById('bidSpread').value),
                    askSpread: parseFloat(document.getElementById('askSpread').value),
                    positionSizeRatio: parseFloat(document.getElementById('positionSizeRatio').value),
                    maxPositionRatio: parseFloat(document.getElementById('maxPositionRatio').value),
                    orderRefreshTime: parseFloat(document.getElementById('orderRefreshTime').value),
                    useDynamicOrderSize: document.getElementById('useDynamicOrderSize').checked,

                    // 🎯 手续费和返佣参数（前端可调）
                    makerFee: parseFloat(document.getElementById('makerFee').value),
                    takerFee: parseFloat(document.getElementById('takerFee').value),
                    useFeeRebate: document.getElementById('useFeeRebate').checked,
                    rebateRate: parseFloat(document.getElementById('rebateRate').value),

                    // 固定参数（与backtest_kline_trajectory.py保持一致）
                    positionMode: "Hedge",
                    minOrderAmount: 0.008,
                    maxOrderAmount: 99.0,
                    positionStopLoss: 0.05,
                    enablePositionStopLoss: false
                };

                // 开始进度监控
                startProgressMonitoring();

                // 发送回测请求
                const response = await fetch(`${BACKEND_URL}/backtest`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(params)
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const result = await response.json();

                // 停止进度监控
                stopProgressMonitoring();

                if (result.success) {
                    updateProgress(100, "回测完成");

                    status.className = 'status success';
                    status.textContent = '回测执行成功！';
                    status.classList.remove('hidden');

                    // 显示结果
                    displayBacktestResults(result);

                    // 显示资金曲线
                    if (result.equity_history) {
                        displayEquityChart(result.equity_history);
                    }

                    // 保存回测结果到全局变量
                    window.currentBacktestResult = result;

                    // 在K线图上添加交易标记
                    if (result.trades) {
                        displayTradeMarkers(result.trades);
                    }

                } else {
                    throw new Error(result.error || '回测失败');
                }

            } catch (error) {
                stopProgressMonitoring();
                updateProgress(0, "回测失败");

                status.className = 'status error';
                status.textContent = `回测失败: ${error.message}`;
                status.classList.remove('hidden');

                console.error('回测失败:', error);
            } finally {
                // 恢复按钮状态
                button.disabled = false;
                button.textContent = '🚀 开始回测';
            }
        }

        // 更新进度
        function updateProgress(percent, message) {
            document.getElementById('progressFill').style.width = percent + '%';
            document.getElementById('progressText').textContent = `${percent}% - ${message}`;
        }

        // 开始进度监控
        function startProgressMonitoring() {
            progressInterval = setInterval(async () => {
                try {
                    const response = await fetch(`${BACKEND_URL}/progress`);
                    const data = await response.json();

                    if (data.progress !== undefined) {
                        updateProgress(data.progress, data.message || '处理中...');
                    }
                } catch (error) {
                    console.error('获取进度失败:', error);
                }
            }, 1000);
        }

        // 停止进度监控
        function stopProgressMonitoring() {
            if (progressInterval) {
                clearInterval(progressInterval);
                progressInterval = null;
            }
        }

        // 显示回测结果
        function displayBacktestResults(result) {
            const resultsPanel = document.getElementById('resultsPanel');
            const metricsGrid = document.getElementById('metricsGrid');

            // 计算指标
            const totalReturnPct = (result.total_return * 100).toFixed(2);
            const maxDrawdownPct = (result.max_drawdown * 100).toFixed(2);
            const winRate = (result.win_rate * 100).toFixed(2);

            // 生成指标卡片
            const metrics = [
                { label: '总收益率', value: `${totalReturnPct}%`, class: totalReturnPct >= 0 ? 'positive' : 'negative' },
                { label: '最大回撤', value: `${maxDrawdownPct}%`, class: 'negative' },
                { label: '胜率', value: `${winRate}%`, class: winRate >= 50 ? 'positive' : 'negative' },
                { label: '总交易次数', value: result.total_trades, class: '' },
                { label: '初始资金', value: `${result.initial_capital} USDT`, class: '' },
                { label: '最终权益', value: `${result.final_equity.toFixed(2)} USDT`, class: result.final_equity >= result.initial_capital ? 'positive' : 'negative' },
                { label: '夏普比率', value: result.sharpe_ratio.toFixed(3), class: result.sharpe_ratio >= 0 ? 'positive' : 'negative' },
                { label: '是否爆仓', value: result.is_liquidated ? '是' : '否', class: result.is_liquidated ? 'negative' : 'positive' }
            ];

            metricsGrid.innerHTML = metrics.map(metric => `
                <div class="metric-card">
                    <div class="metric-label">${metric.label}</div>
                    <div class="metric-value ${metric.class}">${metric.value}</div>
                </div>
            `).join('');

            resultsPanel.classList.remove('hidden');
        }

        // 添加交易标记到K线图
        function addTradeMarkers(trades) {
            if (!candlestickSeries || !trades || trades.length === 0) {
                console.log('没有交易数据或K线图未初始化');
                return;
            }

            console.log(`开始添加 ${trades.length} 个交易标记`);

            const markers = trades.map(trade => {
                let color, position, shape, text;

                // 根据交易类型设置标记样式
                const side = trade.side || '';

                if (side.includes('buy_long') || side === 'BUY_LONG') {
                    color = '#26a69a';
                    position = 'belowBar';
                    shape = 'arrowUp';
                    text = '开多';
                } else if (side.includes('sell_long') || side === 'SELL_LONG') {
                    color = '#ff9800';
                    position = 'aboveBar';
                    shape = 'arrowDown';
                    text = '平多';
                } else if (side.includes('sell_short') || side === 'SELL_SHORT') {
                    color = '#ef5350';
                    position = 'aboveBar';
                    shape = 'arrowDown';
                    text = '开空';
                } else if (side.includes('buy_short') || side === 'BUY_SHORT') {
                    color = '#2196f3';
                    position = 'belowBar';
                    shape = 'arrowUp';
                    text = '平空';
                } else {
                    color = '#9e9e9e';
                    position = 'belowBar';
                    shape = 'circle';
                    text = '交易';
                }

                // 确保时间戳格式正确
                let timestamp = trade.timestamp;
                if (timestamp && timestamp > 1000000000000) {
                    timestamp = Math.floor(timestamp / 1000);
                }

                return {
                    time: timestamp,
                    position: position,
                    color: color,
                    shape: shape,
                    text: text,
                    size: 1
                };
            }).filter(marker => marker.time); // 过滤掉无效时间戳

            console.log(`生成了 ${markers.length} 个有效交易标记`);
            candlestickSeries.setMarkers(markers);
        }
    </script>
</body>
</html>'''
    
    def log_message(self, format, *args):
        """重写日志方法，使用标准日志"""
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    """主函数"""
    port = 3000
    server = HTTPServer(('localhost', port), FrontendHandler)
    
    print("=" * 60)
    print("🌐 永续合约K线回测系统 - 前端服务器启动成功!")
    print("=" * 60)
    print(f"📱 前端地址: http://localhost:{port}")
    print(f"🔗 主页面: http://localhost:{port}/")
    print(f"🔧 API测试: http://localhost:{port}/api/test")
    print(f"🔌 后端服务器: http://localhost:8001")
    print("=" * 60)
    print("按 Ctrl+C 停止服务器")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 前端服务器已停止")
        server.shutdown()

if __name__ == "__main__":
    main()

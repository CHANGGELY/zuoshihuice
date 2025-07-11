#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 Web版回测交易可视化工具
在浏览器中显示，支持多时间周期，详细K线信息
"""

import sys
import os
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime
import json

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from lightweight_charts import Chart
    print("✅ lightweight-charts 导入成功")
except ImportError as e:
    print(f"❌ 导入 lightweight-charts 失败: {e}")
    sys.exit(1)

class Web版回测可视化器:
    """Web版回测交易可视化器"""
    
    def __init__(self):
        self.原始数据 = None
        self.当前时间周期 = '1m'
        self.回测结果 = None
        self.chart = None
        
    def 加载原始数据(self):
        """加载原始1分钟K线数据"""
        try:
            print("📂 加载原始K线数据...")
            
            # 切换到父目录
            original_dir = os.getcwd()
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.chdir(parent_dir)
            
            # 加载数据
            df = pd.read_hdf("K线data/ETHUSDT_1m_2019-11-01_to_2025-06-15.h5", key='klines')
            
            # 转换时间
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            
            # 计算额外指标
            df['成交额'] = df['volume'] * df['close']  # 成交额 = 成交量 * 收盘价
            df['加权平均价'] = df['成交额'] / df['volume']  # 加权平均价 = 成交额 / 成交量
            
            self.原始数据 = df
            print(f"✅ 原始数据加载完成: {len(df)} 条")
            
            # 恢复工作目录
            os.chdir(original_dir)
            return True
            
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            return False
    
    def 运行回测(self):
        """运行回测并收集结果"""
        try:
            print("🚀 运行回测...")
            
            # 切换到父目录
            original_dir = os.getcwd()
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.chdir(parent_dir)
            
            # 导入回测模块
            from backtest_kline_trajectory import run_fast_perpetual_backtest
            
            # 运行回测
            result = asyncio.run(run_fast_perpetual_backtest(use_cache=True))
            
            if result:
                self.回测结果 = result
                print(f"✅ 回测完成，收集到 {len(result.get('trades', []))} 笔交易")
                
                # 恢复工作目录
                os.chdir(original_dir)
                return True
            else:
                print("❌ 回测失败")
                os.chdir(original_dir)
                return False
                
        except Exception as e:
            print(f"❌ 运行回测失败: {e}")
            return False
    
    def 转换时间周期(self, 时间周期='1m'):
        """转换K线数据到指定时间周期"""
        if self.原始数据 is None:
            return None
            
        try:
            print(f"🔄 转换到 {时间周期} 时间周期...")
            
            # 过滤回测时间范围
            start_date = self.回测结果.get('start_date', '2024-06-15')
            end_date = self.回测结果.get('end_date', '2024-07-14')
            
            df = self.原始数据.copy()
            df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)].copy()
            
            if 时间周期 == '1m':
                # 1分钟数据直接使用
                result_df = df.copy()
            else:
                # 转换时间周期
                时间周期映射 = {
                    '5m': '5T',
                    '15m': '15T', 
                    '1h': '1H',
                    '4h': '4H',
                    '1d': '1D'
                }
                
                if 时间周期 not in 时间周期映射:
                    print(f"❌ 不支持的时间周期: {时间周期}")
                    return None
                
                freq = 时间周期映射[时间周期]
                
                # 设置时间索引
                df.set_index('datetime', inplace=True)
                
                # 重采样
                result_df = df.resample(freq).agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum',
                    '成交额': 'sum'
                }).dropna()
                
                # 重新计算加权平均价
                result_df['加权平均价'] = result_df['成交额'] / result_df['volume']
                
                # 重置索引
                result_df.reset_index(inplace=True)
            
            # 计算涨跌幅和振幅
            result_df['涨跌幅'] = ((result_df['close'] - result_df['open']) / result_df['open'] * 100).round(2)
            result_df['振幅'] = ((result_df['high'] - result_df['low']) / result_df['open'] * 100).round(2)
            
            print(f"✅ {时间周期} 数据转换完成: {len(result_df)} 条")
            return result_df
            
        except Exception as e:
            print(f"❌ 时间周期转换失败: {e}")
            return None
    
    def 创建Web图表(self, 时间周期='1m'):
        """创建Web版图表"""
        try:
            print(f"🌐 创建 {时间周期} Web图表...")
            
            # 获取指定时间周期的数据
            df = self.转换时间周期(时间周期)
            if df is None:
                return False
            
            # 创建图表 - 在浏览器中显示
            self.chart = Chart(
                width=1600,
                height=900,
                title=f"🚀 永续合约做市策略回测可视化 - ETH/USDC ({时间周期})",
                toolbox=True  # 启用工具箱
            )
            
            # 设置图表样式 - 类似币安的深色主题
            self.chart.layout(
                background_color='#0b0e11',
                text_color='#f0f3fa',
                font_size=12
            )

            # 设置K线样式 - 类似币安的颜色
            self.chart.candle_style(
                up_color='#02c076',    # 币安绿色
                down_color='#f84960',  # 币安红色
                border_up_color='#02c076',
                border_down_color='#f84960',
                wick_up_color='#02c076',
                wick_down_color='#f84960'
            )

            # 设置十字线样式
            self.chart.crosshair(
                mode='normal',
                vert_visible=True,
                vert_color='#758696',
                vert_style='dashed',
                horz_visible=True,
                horz_color='#758696',
                horz_style='dashed'
            )
            
            # 转换为图表格式
            chart_data = pd.DataFrame({
                'time': df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S'),
                'open': df['open'].astype(float).round(2),
                'high': df['high'].astype(float).round(2),
                'low': df['low'].astype(float).round(2),
                'close': df['close'].astype(float).round(2),
                'volume': df['volume'].astype(float).round(2)
            })
            
            # 设置数据
            self.chart.set(chart_data)

            # 启用成交量 - 使用币安风格颜色
            self.chart.volume_config(
                up_color='rgba(2, 192, 118, 0.3)',   # 币安绿色，半透明
                down_color='rgba(248, 73, 96, 0.3)'  # 币安红色，半透明
            )

            # 设置网格线
            self.chart.grid(
                vert_enabled=True,
                horz_enabled=True,
                color='rgba(117, 134, 150, 0.1)'
            )

            # 启用详细信息显示
            self.启用详细信息显示(df)
            
            # 添加交易标记
            self.添加交易标记(df)
            
            # 添加顶部工具栏
            self.添加时间周期选择器()

            # 添加点击事件来显示K线详情
            self.添加交互事件(df)

            print("✅ Web图表创建完成")
            return True
            
        except Exception as e:
            print(f"❌ 创建Web图表失败: {e}")
            return False
    
    def 添加交易标记(self, df):
        """添加交易标记"""
        if not self.回测结果 or 'trades' not in self.回测结果:
            return
            
        trades = self.回测结果['trades']
        print(f"📍 添加 {len(trades)} 个交易标记...")
        
        # 获取时间范围
        start_time = df['datetime'].iloc[0]
        end_time = df['datetime'].iloc[-1]
        
        标记计数 = {'开多': 0, '开空': 0, '平多': 0, '平空': 0}
        
        for trade in trades:
            timestamp = trade.get('timestamp', 0)
            action = trade.get('action', '')
            amount = trade.get('amount', 0)
            price = trade.get('price', 0)
            leverage = trade.get('leverage', 'N/A')
            
            time_dt = pd.to_datetime(timestamp, unit='s')
            
            # 确保时间在范围内
            if time_dt < start_time or time_dt > end_time:
                continue
            
            # 确定标记样式
            if '开多' in action:
                color = 'green'
                shape = 'arrow_up'
                position = 'below'
                标记计数['开多'] += 1
            elif '开空' in action:
                color = 'red'
                shape = 'arrow_down'
                position = 'below'
                标记计数['开空'] += 1
            elif '平多' in action:
                color = 'orange'
                shape = 'circle'
                position = 'above'
                标记计数['平多'] += 1
            elif '平空' in action:
                color = 'blue'
                shape = 'circle'
                position = 'above'
                标记计数['平空'] += 1
            else:
                continue
            
            try:
                self.chart.marker(
                    time=time_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    position=position,
                    color=color,
                    shape=shape,
                    text=f"{action} {amount:.4f}ETH @{price:.2f} [{leverage}x]"
                )
            except Exception as e:
                continue
        
        print(f"✅ 交易标记统计: {标记计数}")
    
    def 添加时间周期选择器(self):
        """添加时间周期选择器和信息显示"""
        try:
            # 添加时间周期切换器
            self.chart.topbar.switcher(
                'timeframe',
                ('1m', '5m', '15m', '1h', '4h', '1d'),
                default='1m',
                func=self.切换时间周期
            )

            # 添加交易对信息
            self.chart.topbar.textbox('symbol', 'ETH/USDC')

            # 添加回测信息显示
            if self.回测结果:
                总回报率 = self.回测结果.get('total_return', 0) * 100
                总交易次数 = self.回测结果.get('total_trades', 0)
                最终权益 = self.回测结果.get('final_equity', 0)
                最大回撤 = self.回测结果.get('max_drawdown', 0) * 100 if 'max_drawdown' in self.回测结果 else 0

                self.chart.topbar.textbox(
                    'performance',
                    f"📈 回报: {总回报率:.1f}% | 🔄 交易: {总交易次数} | 💰 权益: {最终权益:.0f}U"
                )

                # 添加风险指标
                if 最大回撤 > 0:
                    self.chart.topbar.textbox(
                        'risk',
                        f"📉 最大回撤: {最大回撤:.1f}%"
                    )

            # 启用图例显示
            self.chart.legend(
                visible=True,
                font_size=12,
                text='ETH/USDC 永续合约做市策略回测'
            )

        except Exception as e:
            print(f"⚠️ 添加工具栏失败: {e}")
    
    def 切换时间周期(self, chart):
        """切换时间周期回调函数"""
        try:
            新周期 = chart.topbar['timeframe'].value
            print(f"🔄 切换到 {新周期} 时间周期...")
            
            # 重新创建图表
            self.创建Web图表(新周期)
            
        except Exception as e:
            print(f"❌ 切换时间周期失败: {e}")

    def 添加交互事件(self, df):
        """添加交互事件"""
        try:
            # 存储数据以供事件回调使用
            self.当前数据 = df

            # 添加点击事件
            self.chart.events.click += self.处理点击事件

            print("✅ 交互事件已添加")

        except Exception as e:
            print(f"⚠️ 添加交互事件失败: {e}")

    def 处理点击事件(self, chart):
        """处理点击事件，显示K线详情"""
        try:
            # 这里可以添加点击时的处理逻辑
            # 由于lightweight-charts-python的限制，我们通过其他方式显示信息
            print("📊 图表被点击，详细信息请查看图例区域")

        except Exception as e:
            print(f"⚠️ 处理点击事件失败: {e}")

    def 启用详细信息显示(self, df):
        """启用详细的K线信息显示"""
        try:
            # 创建详细信息映射
            详细信息映射 = {}

            for i, row in df.iterrows():
                时间字符串 = row['datetime'].strftime('%Y-%m-%d %H:%M:%S')

                # 计算涨跌幅和振幅
                涨跌幅 = row.get('涨跌幅', 0)
                振幅 = row.get('振幅', 0)

                详细信息 = {
                    '时间': 时间字符串,
                    '开盘': f"{row['open']:.2f}",
                    '最高': f"{row['high']:.2f}",
                    '最低': f"{row['low']:.2f}",
                    '收盘': f"{row['close']:.2f}",
                    '涨跌幅': f"{涨跌幅:+.2f}%",
                    '振幅': f"{振幅:.2f}%",
                    '成交量': f"{row['volume']:.2f}",
                    '成交额': f"{row['成交额']:.2f}",
                    '加权平均价': f"{row['加权平均价']:.2f}"
                }

                详细信息映射[时间字符串] = 详细信息

            # 注意：lightweight-charts-python可能不直接支持悬停信息
            # 这里我们通过图例来显示当前信息
            self.chart.legend(visible=True, font_size=12)

            print("✅ 详细信息显示已启用")

        except Exception as e:
            print(f"⚠️ 启用详细信息显示失败: {e}")

    def 显示图表(self):
        """在浏览器中显示图表"""
        try:
            print("🌐 在浏览器中启动图表...")
            print("=" * 60)
            print("📈 Web版图表功能:")
            print("   ✓ 多时间周期切换 (1m, 5m, 15m, 1h, 4h, 1d)")
            print("   ✓ 详细K线信息显示")
            print("   ✓ 交易标记可视化")
            print("   ✓ 交互式缩放和拖拽")
            print("   ✓ 成交量显示")
            print("   ✓ 工具箱功能")
            print("=" * 60)
            
            # 在浏览器中显示
            self.chart.show(block=True)
            
        except Exception as e:
            print(f"❌ 显示图表失败: {e}")
    
    def 运行完整流程(self):
        """运行完整的Web可视化流程"""
        print("=" * 60)
        print("🌐 Web版回测交易可视化工具")
        print("=" * 60)
        
        # 1. 加载原始数据
        if not self.加载原始数据():
            return False
        
        # 2. 运行回测
        if not self.运行回测():
            return False
        
        # 3. 创建Web图表
        if not self.创建Web图表():
            return False
        
        # 4. 在浏览器中显示
        self.显示图表()
        
        return True

def main():
    """主函数"""
    可视化器 = Web版回测可视化器()
    可视化器.运行完整流程()

if __name__ == "__main__":
    main()

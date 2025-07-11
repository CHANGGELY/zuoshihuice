#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 标准格式测试 - 按照官方文档格式
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from lightweight_charts import Chart
    print("✅ lightweight-charts 导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    exit(1)

def 创建标准格式数据():
    """按照官方文档创建标准格式数据"""
    print("🔧 创建标准格式数据...")
    
    # 创建时间序列 - 使用字符串格式
    start_time = datetime(2024, 6, 15, 10, 0, 0)
    data = []
    
    for i in range(100):
        time = start_time + timedelta(minutes=i)
        price = 3000 + i * 0.5 + np.sin(i * 0.1) * 20 + np.random.randn() * 5
        
        # 确保 high >= max(open, close) 和 low <= min(open, close)
        open_price = price + np.random.randn() * 2
        close_price = price + np.random.randn() * 2
        high_price = max(open_price, close_price) + abs(np.random.randn() * 3)
        low_price = min(open_price, close_price) - abs(np.random.randn() * 3)
        
        data.append({
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),  # 字符串格式
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2)
        })
    
    df = pd.DataFrame(data)
    print(f"✅ 数据创建完成: {len(df)} 条")
    print(f"   时间: {df['time'].iloc[0]} 到 {df['time'].iloc[-1]}")
    print(f"   价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
    
    # 检查数据完整性
    print("🔍 数据完整性检查:")
    for i, row in df.iterrows():
        if row['high'] < max(row['open'], row['close']) or row['low'] > min(row['open'], row['close']):
            print(f"⚠️ 第{i}行数据异常: high={row['high']}, low={row['low']}, open={row['open']}, close={row['close']}")
    
    return df

def 测试标准格式图表():
    """测试标准格式图表"""
    try:
        # 创建数据
        df = 创建标准格式数据()
        
        # 创建图表
        chart = Chart(
            width=1200,
            height=800,
            title="🔧 标准格式测试图表"
        )
        
        print("📊 设置数据到图表...")
        # 直接设置DataFrame，不需要设置索引
        chart.set(df)
        
        print("📍 添加测试标记...")
        # 添加标记 - 使用字符串时间格式
        chart.marker(
            time=df.iloc[20]['time'],
            position='below',
            color='green',
            shape='arrow_up',
            text=f'开多 @{df.iloc[20]["close"]:.2f}'
        )
        
        chart.marker(
            time=df.iloc[50]['time'],
            position='below',
            color='red',
            shape='arrow_down',
            text=f'开空 @{df.iloc[50]["close"]:.2f}'
        )
        
        chart.marker(
            time=df.iloc[80]['time'],
            position='above',
            color='orange',
            shape='circle',
            text=f'平仓 @{df.iloc[80]["close"]:.2f}'
        )
        
        print("✅ 标记添加完成")
        print("🌐 启动图表...")
        
        # 显示图表
        chart.show(block=True)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def 测试真实数据():
    """测试真实K线数据"""
    try:
        print("📂 测试真实K线数据...")
        
        # 切换到父目录
        original_dir = os.getcwd()
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(parent_dir)
        
        # 加载数据
        df = pd.read_hdf("K线data/ETHUSDT_1m_2019-11-01_to_2025-06-15.h5", key='klines')
        
        # 过滤两周数据
        start_date = '2024-06-15'
        end_date = '2024-06-29'
        
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)].copy()
        
        # 限制数据量
        df = df.head(1000)
        
        # 转换为标准格式
        df_chart = pd.DataFrame({
            'time': df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S'),
            'open': df['open'].astype(float).round(2),
            'high': df['high'].astype(float).round(2),
            'low': df['low'].astype(float).round(2),
            'close': df['close'].astype(float).round(2)
        })
        
        print(f"✅ 真实数据准备完成: {len(df_chart)} 条")
        print(f"   时间: {df_chart['time'].iloc[0]} 到 {df_chart['time'].iloc[-1]}")
        print(f"   价格: {df_chart['close'].min():.2f} - {df_chart['close'].max():.2f}")
        
        # 创建图表
        chart = Chart(
            width=1400,
            height=900,
            title="🔧 真实K线数据测试 - ETH/USDT"
        )
        
        # 设置数据
        chart.set(df_chart)
        
        # 添加几个标记
        mid = len(df_chart) // 2
        quarter = len(df_chart) // 4
        
        chart.marker(
            time=df_chart.iloc[quarter]['time'],
            position='below',
            color='green',
            shape='arrow_up',
            text=f'测试开多 @{df_chart.iloc[quarter]["close"]:.2f}'
        )
        
        chart.marker(
            time=df_chart.iloc[mid]['time'],
            position='below',
            color='red',
            shape='arrow_down',
            text=f'测试开空 @{df_chart.iloc[mid]["close"]:.2f}'
        )
        
        print("✅ 真实数据图表准备完成")
        print("🌐 启动图表...")
        
        chart.show(block=True)
        
    except Exception as e:
        print(f"❌ 真实数据测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            os.chdir(original_dir)
        except:
            pass

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 标准格式测试工具")
    print("=" * 60)
    print("选择测试模式:")
    print("1. 标准格式模拟数据")
    print("2. 真实K线数据")
    print("=" * 60)
    
    # 直接测试真实数据
    测试真实数据()

if __name__ == "__main__":
    main()

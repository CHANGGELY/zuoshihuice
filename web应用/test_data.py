#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据加载
"""

import sys
import os
from pathlib import Path

# 添加backend路径
backend_path = Path(__file__).parent / 'backend'
sys.path.append(str(backend_path))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_platform.settings')

import django
django.setup()

from market_data.services import MarketDataService

def test_data_loading():
    """测试数据加载"""
    print("🔍 测试H5数据文件加载...")
    
    service = MarketDataService()
    
    # 测试加载数据
    data = service.load_kline_data('ETHUSDT', '1m')
    
    if data is not None:
        print(f"✅ 成功加载数据，共 {len(data)} 条记录")
        print(f"时间范围: {data['datetime'].min()} 到 {data['datetime'].max()}")
        print(f"数据列: {list(data.columns)}")
        print(f"前5行数据:")
        print(data.head())
        
        # 测试API方法
        print("\n🔍 测试API方法...")
        kline_data = service.get_kline_data(
            symbol='ETHUSDT',
            timeframe='1m',
            start_date='2024-06-15',
            end_date='2024-06-16',
            limit=100
        )
        
        print(f"✅ API返回 {len(kline_data)} 条K线数据")
        if kline_data:
            print("示例数据:", kline_data[0])
        
        # 测试市场统计
        print("\n🔍 测试市场统计...")
        stats = service.get_market_stats('ETHUSDT')
        print(f"✅ 市场统计: {stats}")
        
    else:
        print("❌ 数据加载失败")

if __name__ == "__main__":
    test_data_loading()

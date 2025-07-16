#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试返佣计算问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest_kline_trajectory import calculate_monthly_rebates_from_trades, REBATE_CONFIG
import datetime

def test_rebate_with_sample_data():
    """使用示例数据测试返佣计算"""
    print("🧪 测试返佣计算")
    print("="*50)
    
    # 创建示例交易数据
    sample_trades = []
    
    # 2020年1月的交易
    jan_start = datetime.datetime(2020, 1, 15).timestamp()
    jan_end = datetime.datetime(2020, 1, 25).timestamp()
    
    # 2020年2月的交易
    feb_start = datetime.datetime(2020, 2, 10).timestamp()
    feb_end = datetime.datetime(2020, 2, 20).timestamp()
    
    # 2020年3月的交易
    mar_start = datetime.datetime(2020, 3, 5).timestamp()
    mar_end = datetime.datetime(2020, 3, 15).timestamp()
    
    # 添加示例交易
    for i in range(10):
        # 1月交易
        sample_trades.append({
            'timestamp': jan_start + i * 3600,  # 每小时一笔
            'fee': 0.5,  # 0.5 USDT手续费
            'side': 'buy' if i % 2 == 0 else 'sell'
        })
        
        # 2月交易
        sample_trades.append({
            'timestamp': feb_start + i * 3600,
            'fee': 0.3,
            'side': 'buy' if i % 2 == 0 else 'sell'
        })
        
        # 3月交易
        sample_trades.append({
            'timestamp': mar_start + i * 3600,
            'fee': 0.4,
            'side': 'buy' if i % 2 == 0 else 'sell'
        })
    
    print(f"📊 创建了 {len(sample_trades)} 条示例交易")
    
    # 显示交易分布
    print("\n📅 交易时间分布:")
    for trade in sample_trades[:5]:  # 显示前5条
        trade_date = datetime.datetime.fromtimestamp(trade['timestamp'])
        print(f"  {trade_date.strftime('%Y-%m-%d %H:%M')} - 手续费: {trade['fee']} USDT")
    print("  ...")
    
    # 计算返佣
    print(f"\n💰 返佣配置:")
    print(f"  启用返佣: {REBATE_CONFIG['use_fee_rebate']}")
    print(f"  返佣率: {float(REBATE_CONFIG['rebate_rate'])*100}%")
    print(f"  发放日: {REBATE_CONFIG['rebate_payout_day']}号")
    print(f"  汇率: {REBATE_CONFIG['usd_to_rmb_rate']}")
    
    # 调用返佣计算函数
    rebates = calculate_monthly_rebates_from_trades(sample_trades)
    
    print(f"\n📈 返佣结果:")
    if rebates:
        for timestamp, amount in rebates:
            payout_date = datetime.datetime.fromtimestamp(timestamp)
            print(f"  {payout_date.strftime('%Y-%m-%d')}: ¥{amount:.2f}")
    else:
        print("  ❌ 没有返佣数据")
    
    return rebates

def analyze_rebate_logic():
    """分析返佣逻辑"""
    print("\n🔍 返佣逻辑分析")
    print("-"*30)
    
    # 测试不同日期的返佣周期计算
    test_dates = [
        datetime.datetime(2020, 1, 10),  # 1月10号 -> 1月19号发放
        datetime.datetime(2020, 1, 18),  # 1月18号 -> 2月19号发放
        datetime.datetime(2020, 1, 19),  # 1月19号 -> 2月19号发放
        datetime.datetime(2020, 1, 25),  # 1月25号 -> 2月19号发放
        datetime.datetime(2020, 2, 15),  # 2月15号 -> 2月19号发放
        datetime.datetime(2020, 2, 18),  # 2月18号 -> 3月19号发放
    ]
    
    payout_day = REBATE_CONFIG["rebate_payout_day"]
    
    print(f"返佣周期规则: 上月18号到本月18号的手续费，在本月{payout_day}号发放")
    print("\n测试日期 -> 发放日期:")
    
    for trade_date in test_dates:
        # 计算发放日期（复制原函数逻辑）
        if trade_date.day >= 18:
            # 18号及以后的交易，属于下个月19号发放的周期
            if trade_date.month == 12:
                payout_date = datetime.datetime(trade_date.year + 1, 1, payout_day)
            else:
                payout_date = datetime.datetime(trade_date.year, trade_date.month + 1, payout_day)
        else:
            # 18号之前的交易，属于本月19号发放的周期
            payout_date = datetime.datetime(trade_date.year, trade_date.month, payout_day)
        
        print(f"  {trade_date.strftime('%Y-%m-%d')} -> {payout_date.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    analyze_rebate_logic()
    test_rebate_with_sample_data()

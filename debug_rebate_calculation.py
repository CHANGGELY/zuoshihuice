#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试返佣计算问题
检查为什么后面的月返佣都是0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest_kline_trajectory import *
import datetime
from collections import defaultdict

def debug_rebate_calculation():
    """调试返佣计算过程"""
    print("🔍 调试返佣计算问题")
    print("="*60)
    
    # 先运行一个简短的回测获取交易历史
    print("📊 运行回测获取交易历史...")
    
    # 检查当前配置
    print(f"当前配置: {BACKTEST_CONFIG['start_date']} 到 {BACKTEST_CONFIG['end_date']}")
    print(f"杠杆: {STRATEGY_CONFIG['leverage']}x")
    
    try:
        # 运行回测
        exchange = Exchange()
        strategy = GridTradingStrategy(exchange)
        
        # 加载数据
        print("📂 加载数据...")
        data_loader = DataLoader()
        kline_data = data_loader.load_data(
            BACKTEST_CONFIG["start_date"], 
            BACKTEST_CONFIG["end_date"]
        )
        
        if not kline_data:
            print("❌ 无法加载数据")
            return
            
        print(f"✅ 加载了 {len(kline_data)} 条K线数据")
        
        # 运行回测（只运行一小部分来获取交易历史）
        print("🚀 运行回测...")
        for i, kline in enumerate(kline_data[:50000]):  # 只运行前50000条
            if i % 10000 == 0:
                print(f"进度: {i}/{len(kline_data)}")
            
            timestamp = int(kline['timestamp'])
            price = Decimal(str(kline['close']))
            
            exchange.update_price(timestamp, price)
            strategy.on_tick(timestamp, price)
            
            if len(exchange.trade_history) > 100:  # 有足够的交易记录就停止
                break
        
        print(f"✅ 获得 {len(exchange.trade_history)} 条交易记录")
        
        # 分析交易历史
        analyze_trade_history(exchange.trade_history)
        
        # 测试返佣计算
        test_rebate_calculation(exchange.trade_history)
        
    except Exception as e:
        print(f"❌ 调试过程出错: {e}")
        import traceback
        traceback.print_exc()

def analyze_trade_history(trade_history):
    """分析交易历史分布"""
    print("\n📈 交易历史分析")
    print("-"*40)
    
    if not trade_history:
        print("❌ 没有交易历史")
        return
    
    # 按月统计交易
    monthly_stats = defaultdict(lambda: {'count': 0, 'total_fee': 0})
    
    for trade in trade_history:
        timestamp = trade.get('timestamp', 0)
        fee = float(trade.get('fee', 0))
        
        if timestamp > 0:
            trade_date = datetime.datetime.fromtimestamp(timestamp)
            month_key = f"{trade_date.year}-{trade_date.month:02d}"
            
            monthly_stats[month_key]['count'] += 1
            monthly_stats[month_key]['total_fee'] += fee
    
    print("月度交易统计:")
    for month, stats in sorted(monthly_stats.items()):
        print(f"  {month}: {stats['count']} 笔交易, 总手续费: {stats['total_fee']:.4f} USDT")

def test_rebate_calculation(trade_history):
    """测试返佣计算详细过程"""
    print("\n💰 返佣计算测试")
    print("-"*40)
    
    if not trade_history:
        print("❌ 没有交易历史")
        return
    
    # 手动计算返佣，添加调试信息
    rebate_rate = float(REBATE_CONFIG["rebate_rate"])
    usd_to_rmb = REBATE_CONFIG["usd_to_rmb_rate"]
    payout_day = REBATE_CONFIG["rebate_payout_day"]
    
    print(f"返佣配置:")
    print(f"  返佣率: {rebate_rate*100}%")
    print(f"  汇率: {usd_to_rmb}")
    print(f"  发放日: 每月{payout_day}号")
    
    # 按返佣周期统计手续费
    period_fees = defaultdict(float)
    
    print(f"\n处理 {len(trade_history)} 条交易记录:")
    
    for i, trade in enumerate(trade_history[:10]):  # 只显示前10条
        trade_timestamp = trade.get('timestamp', 0)
        trade_fee = float(trade.get('fee', 0))
        
        if trade_timestamp <= 0 or trade_fee <= 0:
            continue
            
        trade_date = datetime.datetime.fromtimestamp(trade_timestamp)
        
        # 确定返佣周期
        if trade_date.day >= 18:
            if trade_date.month == 12:
                payout_date = datetime.datetime(trade_date.year + 1, 1, payout_day)
            else:
                payout_date = datetime.datetime(trade_date.year, trade_date.month + 1, payout_day)
        else:
            payout_date = datetime.datetime(trade_date.year, trade_date.month, payout_day)
        
        payout_timestamp = payout_date.timestamp()
        period_fees[payout_timestamp] += trade_fee
        
        print(f"  交易{i+1}: {trade_date.strftime('%Y-%m-%d %H:%M')} -> 返佣发放: {payout_date.strftime('%Y-%m-%d')}, 手续费: {trade_fee:.4f}")
    
    # 计算返佣
    print(f"\n返佣计算结果:")
    rebates = []
    for payout_timestamp, total_period_fees in sorted(period_fees.items()):
        payout_date = datetime.datetime.fromtimestamp(payout_timestamp)
        rebate_amount_usd = total_period_fees * rebate_rate
        rebate_amount_rmb = rebate_amount_usd * usd_to_rmb
        
        print(f"  {payout_date.strftime('%Y-%m-%d')}: 手续费 {total_period_fees:.4f} USDT -> 返佣 ¥{rebate_amount_rmb:.2f}")
        
        if total_period_fees > 0:
            rebates.append((payout_timestamp, rebate_amount_rmb))
    
    print(f"\n最终返佣数据点: {len(rebates)} 个")
    
    # 调用原始函数对比
    original_rebates = calculate_monthly_rebates_from_trades(trade_history)
    print(f"原始函数返回: {len(original_rebates)} 个数据点")
    
    if len(original_rebates) != len(rebates):
        print("⚠️ 数据点数量不匹配!")
    else:
        print("✅ 数据点数量匹配")

if __name__ == "__main__":
    debug_rebate_calculation()

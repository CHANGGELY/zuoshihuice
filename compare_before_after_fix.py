#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比修复前后的差异
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest_kline_trajectory import *
import datetime

def compare_logic():
    """对比修复前后的逻辑差异"""
    print("🔍 对比修复前后的逻辑差异")
    print("="*60)
    
    # 测试参数
    initial_balance = 1000  # USDT
    eth_price = 2000  # USDT
    leverage_5x = 5
    leverage_125x = 125
    
    print(f"测试条件:")
    print(f"  初始资金: {initial_balance} USDT")
    print(f"  ETH价格: {eth_price} USDT")
    print(f"  手续费率: {float(MARKET_CONFIG['maker_fee'])*100:.3f}%")
    
    print(f"\n📊 修复前的错误逻辑:")
    print(f"{'杠杆':<8} {'保证金':<12} {'下单量(ETH)':<15} {'手续费':<12} {'返佣(¥)':<10}")
    print("-" * 65)
    
    # 修复前的错误逻辑
    for leverage in [leverage_5x, leverage_125x]:
        # 错误的计算方式
        margin_amount = initial_balance / leverage  # 保证金金额
        order_amount_eth = margin_amount / eth_price  # 基于保证金的ETH数量
        wrong_fee = margin_amount * float(MARKET_CONFIG['maker_fee'])  # 错误：基于保证金计算手续费
        wrong_rebate = wrong_fee * float(REBATE_CONFIG['rebate_rate']) * REBATE_CONFIG['usd_to_rmb_rate']
        
        print(f"{leverage:<8}x {margin_amount:<12.2f} {order_amount_eth:<15.6f} {wrong_fee:<12.6f} {wrong_rebate:<10.2f}")
    
    print(f"\n✅ 修复后的正确逻辑:")
    print(f"{'杠杆':<8} {'开仓价值':<12} {'下单量(ETH)':<15} {'手续费':<12} {'返佣(¥)':<10}")
    print("-" * 65)
    
    # 修复后的正确逻辑
    target_position_value = initial_balance * 0.01  # 每次开仓1%权益
    
    for leverage in [leverage_5x, leverage_125x]:
        # 正确的计算方式
        position_value = target_position_value  # 目标开仓价值
        order_amount_eth = position_value / eth_price  # 基于开仓价值的ETH数量
        correct_fee = position_value * float(MARKET_CONFIG['maker_fee'])  # 正确：基于开仓价值计算手续费
        correct_rebate = correct_fee * float(REBATE_CONFIG['rebate_rate']) * REBATE_CONFIG['usd_to_rmb_rate']
        
        print(f"{leverage:<8}x {position_value:<12.2f} {order_amount_eth:<15.6f} {correct_fee:<12.6f} {correct_rebate:<10.2f}")
    
    print(f"\n💡 关键差异:")
    print(f"1. 修复前：不同杠杆的手续费不同，导致返佣差异巨大")
    print(f"2. 修复后：相同开仓价值的手续费相同，返佣计算正确")
    print(f"3. 这解释了为什么5x杠杆的返佣比125x杠杆少很多")

def analyze_actual_impact():
    """分析实际影响"""
    print(f"\n📈 实际影响分析:")
    print("-" * 40)
    
    # 假设一个月有1000笔交易
    monthly_trades = 1000
    
    print(f"假设一个月有 {monthly_trades} 笔交易:")
    
    # 修复前的错误计算
    wrong_fee_5x = (1000 / 5) * float(MARKET_CONFIG['maker_fee']) * monthly_trades
    wrong_fee_125x = (1000 / 125) * float(MARKET_CONFIG['maker_fee']) * monthly_trades
    
    wrong_rebate_5x = wrong_fee_5x * float(REBATE_CONFIG['rebate_rate']) * REBATE_CONFIG['usd_to_rmb_rate']
    wrong_rebate_125x = wrong_fee_125x * float(REBATE_CONFIG['rebate_rate']) * REBATE_CONFIG['usd_to_rmb_rate']
    
    print(f"\n修复前 (错误逻辑):")
    print(f"  5x杠杆月手续费: {wrong_fee_5x:.2f} USDT -> 返佣 ¥{wrong_rebate_5x:.2f}")
    print(f"  125x杠杆月手续费: {wrong_fee_125x:.2f} USDT -> 返佣 ¥{wrong_rebate_125x:.2f}")
    print(f"  差异: {wrong_rebate_5x/wrong_rebate_125x:.1f}倍")
    
    # 修复后的正确计算
    target_position_value = 1000 * 0.01  # 每次1%权益
    correct_fee = target_position_value * float(MARKET_CONFIG['maker_fee']) * monthly_trades
    correct_rebate = correct_fee * float(REBATE_CONFIG['rebate_rate']) * REBATE_CONFIG['usd_to_rmb_rate']
    
    print(f"\n修复后 (正确逻辑):")
    print(f"  任何杠杆月手续费: {correct_fee:.2f} USDT -> 返佣 ¥{correct_rebate:.2f}")
    print(f"  所有杠杆返佣相同 ✅")
    
    print(f"\n🎯 结论:")
    print(f"修复前5x杠杆的返佣被严重低估了 {wrong_rebate_5x/correct_rebate:.1f}倍!")
    print(f"修复后所有杠杆的返佣计算都正确了!")

if __name__ == "__main__":
    compare_logic()
    analyze_actual_impact()

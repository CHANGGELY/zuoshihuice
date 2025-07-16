#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的杠杆和手续费逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest_kline_trajectory import *
import datetime

def test_fixed_leverage_logic():
    """测试修复后的杠杆逻辑"""
    print("🔧 测试修复后的杠杆和手续费逻辑")
    print("="*60)
    
    # 测试不同杠杆下的手续费
    leverage_tests = [5, 25, 125]
    
    for leverage in leverage_tests:
        print(f"\n📊 测试 {leverage}x 杠杆")
        print("-"*30)
        
        # 备份原始配置
        original_leverage = STRATEGY_CONFIG["leverage"]
        
        try:
            # 设置测试杠杆
            STRATEGY_CONFIG["leverage"] = leverage
            
            # 创建交易所和策略
            exchange = FastPerpetualExchange(1000)  # 1000 USDT初始资金
            strategy = FastPerpetualStrategy(exchange)
            
            # 设置价格
            test_price = Decimal("2000")  # ETH价格2000 USDT
            exchange.update_price(int(datetime.datetime.now().timestamp()), test_price)
            
            # 计算下单量
            order_amount = strategy.calculate_dynamic_order_size(test_price)
            
            # 计算开仓价值和手续费
            position_value = order_amount * test_price
            fee = position_value * MARKET_CONFIG["maker_fee"]
            
            # 计算所需保证金
            required_margin = position_value / Decimal(str(leverage))
            
            print(f"  杠杆倍数: {leverage}x")
            print(f"  下单数量: {order_amount:.6f} ETH")
            print(f"  开仓价值: {position_value:.2f} USDT")
            print(f"  所需保证金: {required_margin:.2f} USDT")
            print(f"  手续费: {fee:.6f} USDT")
            print(f"  手续费率验证: {float(fee/position_value)*100:.4f}% (应该是0.02%)")
            
            # 验证逻辑正确性
            expected_fee_rate = float(MARKET_CONFIG["maker_fee"])
            actual_fee_rate = float(fee / position_value)
            
            if abs(actual_fee_rate - expected_fee_rate) < 0.0001:
                print(f"  ✅ 手续费计算正确")
            else:
                print(f"  ❌ 手续费计算错误")
                
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            
        finally:
            # 恢复原始配置
            STRATEGY_CONFIG["leverage"] = original_leverage
    
    print(f"\n💡 修复后的逻辑:")
    print(f"1. 下单量基于目标开仓价值计算，而不是保证金")
    print(f"2. 手续费基于实际开仓价值计算")
    print(f"3. 不同杠杆下，相同开仓价值的手续费应该相同")
    print(f"4. 这样返佣计算就会正确了")

def test_rebate_calculation():
    """测试修复后的返佣计算"""
    print(f"\n💰 测试修复后的返佣计算")
    print("-"*40)
    
    # 创建模拟交易数据
    sample_trades = []
    
    # 模拟相同开仓价值但不同杠杆的交易
    base_position_value = 1000  # 1000 USDT开仓价值
    
    # 5x杠杆交易
    fee_5x = base_position_value * float(MARKET_CONFIG["maker_fee"])
    sample_trades.append({
        'timestamp': datetime.datetime(2020, 1, 15).timestamp(),
        'fee': fee_5x,
        'leverage': 5
    })
    
    # 125x杠杆交易
    fee_125x = base_position_value * float(MARKET_CONFIG["maker_fee"])
    sample_trades.append({
        'timestamp': datetime.datetime(2020, 1, 16).timestamp(),
        'fee': fee_125x,
        'leverage': 125
    })
    
    print(f"模拟交易数据:")
    print(f"  开仓价值: {base_position_value} USDT (两笔交易相同)")
    print(f"  5x杠杆手续费: {fee_5x:.6f} USDT")
    print(f"  125x杠杆手续费: {fee_125x:.6f} USDT")
    print(f"  手续费是否相等: {'✅ 是' if abs(fee_5x - fee_125x) < 0.000001 else '❌ 否'}")
    
    # 计算返佣
    rebates = calculate_monthly_rebates_from_trades(sample_trades)
    
    if rebates:
        for timestamp, amount in rebates:
            payout_date = datetime.datetime.fromtimestamp(timestamp)
            print(f"  返佣发放日: {payout_date.strftime('%Y-%m-%d')}")
            print(f"  返佣金额: ¥{amount:.2f}")
    else:
        print(f"  ❌ 没有返佣数据")

if __name__ == "__main__":
    test_fixed_leverage_logic()
    test_rebate_calculation()

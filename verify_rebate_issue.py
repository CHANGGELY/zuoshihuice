#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证返佣问题的根本原因
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest_kline_trajectory import *
import datetime

def verify_rebate_issue():
    """验证返佣问题"""
    print("🔍 验证返佣问题的根本原因")
    print("="*60)
    
    print("📊 当前配置:")
    print(f"  时间范围: {BACKTEST_CONFIG['start_date']} 到 {BACKTEST_CONFIG['end_date']}")
    print(f"  杠杆: {STRATEGY_CONFIG['leverage']}x")
    print(f"  返佣率: {float(REBATE_CONFIG['rebate_rate'])*100}%")
    
    # 计算时间范围内应该有多少个返佣发放日
    start_date = datetime.datetime.strptime(BACKTEST_CONFIG['start_date'], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(BACKTEST_CONFIG['end_date'], '%Y-%m-%d')
    
    payout_day = REBATE_CONFIG['rebate_payout_day']
    expected_payouts = []
    
    current_date = start_date.replace(day=1)  # 从开始月份的1号开始
    while current_date <= end_date:
        try:
            payout_date = current_date.replace(day=payout_day)
            if start_date <= payout_date <= end_date:
                expected_payouts.append(payout_date.strftime('%Y-%m-%d'))
        except ValueError:
            pass  # 处理2月29日等特殊情况
        
        # 移动到下个月
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    print(f"\n📅 预期返佣发放日期 ({len(expected_payouts)} 个):")
    for payout in expected_payouts:
        print(f"  {payout}")
    
    # 分析杠杆对交易的影响
    print(f"\n⚖️ 杠杆影响分析:")
    leverage = STRATEGY_CONFIG['leverage']
    initial_balance = BACKTEST_CONFIG['initial_balance']
    
    # 计算每次下单金额
    position_size_ratio = 1 / leverage  # 动态计算
    order_amount = initial_balance * position_size_ratio
    
    print(f"  初始资金: {initial_balance} USDT")
    print(f"  杠杆倍数: {leverage}x")
    print(f"  仓位比例: {position_size_ratio:.4f} ({position_size_ratio*100:.2f}%)")
    print(f"  每次下单金额: {order_amount:.2f} USDT")
    
    # 估算手续费
    maker_fee_rate = float(MARKET_CONFIG['maker_fee'])
    taker_fee_rate = float(MARKET_CONFIG['taker_fee'])
    
    print(f"  挂单手续费率: {maker_fee_rate*100:.3f}%")
    print(f"  吃单手续费率: {taker_fee_rate*100:.3f}%")
    print(f"  每笔挂单手续费: {order_amount * maker_fee_rate:.4f} USDT")
    print(f"  每笔吃单手续费: {order_amount * taker_fee_rate:.4f} USDT")
    
    # 估算需要多少笔交易才能产生有意义的返佣
    min_rebate_rmb = 1.0  # 最小1元返佣
    rebate_rate = float(REBATE_CONFIG['rebate_rate'])
    usd_to_rmb = REBATE_CONFIG['usd_to_rmb_rate']
    
    min_fee_usd = min_rebate_rmb / (rebate_rate * usd_to_rmb)
    min_trades_maker = min_fee_usd / (order_amount * maker_fee_rate)
    min_trades_taker = min_fee_usd / (order_amount * taker_fee_rate)
    
    print(f"\n💰 返佣阈值分析:")
    print(f"  最小有意义返佣: ¥{min_rebate_rmb}")
    print(f"  需要最小手续费: {min_fee_usd:.4f} USDT")
    print(f"  需要挂单交易: {min_trades_maker:.0f} 笔")
    print(f"  需要吃单交易: {min_trades_taker:.0f} 笔")
    
    print(f"\n💡 结论:")
    print(f"1. 当前杠杆 {leverage}x 相对较低，每次下单金额较大但交易频率可能较低")
    print(f"2. 如果某个月交易次数少于 {min_trades_maker:.0f} 笔，返佣可能低于¥1")
    print(f"3. 时间范围只到 {BACKTEST_CONFIG['end_date']}，后面月份自然没有数据")
    print(f"4. 建议检查实际交易记录，确认是否真的交易频率过低")

def suggest_solutions():
    """建议解决方案"""
    print(f"\n🛠️ 建议解决方案:")
    print(f"1. 如果想看到更多返佣数据:")
    print(f"   - 延长回测时间范围到全年 (end_date: '2020-12-31')")
    print(f"   - 或者提高杠杆增加交易频率 (leverage: 25-50)")
    
    print(f"\n2. 如果想验证返佣计算正确性:")
    print(f"   - 可以手动检查某个月的交易记录和手续费")
    print(f"   - 确认返佣计算公式: 返佣 = 手续费 × 30% × 7.2汇率")
    
    print(f"\n3. 如果返佣显示为0是正常的:")
    print(f"   - 低杠杆策略交易频率本来就低")
    print(f"   - 某些月份交易少，返佣自然就少")
    print(f"   - 这反映了真实的交易情况")

if __name__ == "__main__":
    verify_rebate_issue()
    suggest_solutions()

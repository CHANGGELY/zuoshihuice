#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析杠杆对交易频率和返佣的影响
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest_kline_trajectory import *
import datetime

def compare_leverage_impact():
    """比较不同杠杆下的交易频率"""
    print("🔍 分析杠杆对交易频率和返佣的影响")
    print("="*60)
    
    # 测试两种杠杆设置
    leverage_tests = [
        {"leverage": 5, "name": "低杠杆(5x)"},
        {"leverage": 125, "name": "高杠杆(125x)"}
    ]
    
    for test in leverage_tests:
        print(f"\n📊 测试 {test['name']}")
        print("-"*40)
        
        # 备份原始配置
        original_leverage = STRATEGY_CONFIG["leverage"]
        
        try:
            # 设置测试杠杆
            STRATEGY_CONFIG["leverage"] = test["leverage"]
            
            # 创建交易所和策略
            exchange = Exchange()
            strategy = GridTradingStrategy(exchange)
            
            # 加载少量数据进行测试
            data_loader = DataLoader()
            kline_data = data_loader.load_data("2020-01-01", "2020-01-31")  # 只测试1月
            
            if not kline_data:
                print("❌ 无法加载数据")
                continue
            
            print(f"✅ 加载了 {len(kline_data)} 条K线数据")
            
            # 运行回测
            trade_count = 0
            total_fees = 0
            
            for i, kline in enumerate(kline_data):
                if i > 10000:  # 只运行前10000条
                    break
                    
                timestamp = int(kline['timestamp'])
                price = Decimal(str(kline['close']))
                
                exchange.update_price(timestamp, price)
                
                # 记录交易前的数量
                prev_trade_count = len(exchange.trade_history)
                
                strategy.on_tick(timestamp, price)
                
                # 计算新增交易
                new_trades = len(exchange.trade_history) - prev_trade_count
                trade_count += new_trades
                
                # 计算总手续费
                for j in range(prev_trade_count, len(exchange.trade_history)):
                    total_fees += float(exchange.trade_history[j].get('fee', 0))
            
            print(f"📈 结果:")
            print(f"  总交易次数: {trade_count}")
            print(f"  总手续费: {total_fees:.4f} USDT")
            print(f"  平均每笔手续费: {total_fees/trade_count if trade_count > 0 else 0:.4f} USDT")
            
            # 计算预期返佣
            if total_fees > 0:
                rebate_rate = float(REBATE_CONFIG["rebate_rate"])
                usd_to_rmb = REBATE_CONFIG["usd_to_rmb_rate"]
                expected_rebate = total_fees * rebate_rate * usd_to_rmb
                print(f"  预期月返佣: ¥{expected_rebate:.2f}")
            else:
                print(f"  预期月返佣: ¥0.00")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            
        finally:
            # 恢复原始配置
            STRATEGY_CONFIG["leverage"] = original_leverage
    
    print(f"\n💡 分析结论:")
    print(f"1. 杠杆越低，每次下单金额越大（因为 position_size = balance / leverage）")
    print(f"2. 但是杠杆越低，触发交易的频率可能越低")
    print(f"3. 手续费 = 交易金额 × 手续费率，所以总手续费取决于交易频率和单笔金额")
    print(f"4. 如果交易频率大幅下降，总手续费可能减少，导致返佣减少")

def check_actual_rebate_data():
    """检查实际的返佣数据"""
    print(f"\n🔍 检查实际返佣数据")
    print("-"*30)
    
    # 运行一个快速回测获取真实数据
    try:
        exchange = Exchange()
        strategy = GridTradingStrategy(exchange)
        
        data_loader = DataLoader()
        kline_data = data_loader.load_data("2020-01-01", "2020-02-29")  # 2个月数据
        
        if not kline_data:
            print("❌ 无法加载数据")
            return
        
        print(f"✅ 加载了 {len(kline_data)} 条K线数据")
        
        # 运行回测
        for i, kline in enumerate(kline_data):
            if i % 20000 == 0:
                print(f"进度: {i}/{len(kline_data)}")
                
            timestamp = int(kline['timestamp'])
            price = Decimal(str(kline['close']))
            
            exchange.update_price(timestamp, price)
            strategy.on_tick(timestamp, price)
        
        print(f"✅ 回测完成，共 {len(exchange.trade_history)} 笔交易")
        
        # 分析交易分布
        if exchange.trade_history:
            monthly_fees = {}
            for trade in exchange.trade_history:
                timestamp = trade.get('timestamp', 0)
                fee = float(trade.get('fee', 0))
                
                if timestamp > 0:
                    trade_date = datetime.datetime.fromtimestamp(timestamp)
                    month_key = f"{trade_date.year}-{trade_date.month:02d}"
                    
                    if month_key not in monthly_fees:
                        monthly_fees[month_key] = 0
                    monthly_fees[month_key] += fee
            
            print(f"\n📊 月度手续费统计:")
            for month, fees in sorted(monthly_fees.items()):
                rebate_rate = float(REBATE_CONFIG["rebate_rate"])
                usd_to_rmb = REBATE_CONFIG["usd_to_rmb_rate"]
                rebate = fees * rebate_rate * usd_to_rmb
                print(f"  {month}: 手续费 {fees:.4f} USDT -> 返佣 ¥{rebate:.2f}")
        
        # 调用返佣计算函数
        rebates = calculate_monthly_rebates_from_trades(exchange.trade_history)
        print(f"\n💰 返佣计算结果: {len(rebates)} 个数据点")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_leverage_impact()
    check_actual_rebate_data()

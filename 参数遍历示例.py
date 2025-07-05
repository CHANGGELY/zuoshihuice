#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数遍历回测示例
演示如何使用缓存系统快速遍历不同的策略参数组合
"""

import asyncio
from decimal import Decimal
from backtest_kline_trajectory import run_backtest_with_params
import pandas as pd

def 参数遍历回测():
    """遍历不同的策略参数组合进行回测"""
    
    print("=== 🔄 参数遍历回测系统 ===")
    print("利用数据缓存机制，快速测试不同参数组合")
    print()
    
    # 定义要测试的参数组合
    参数组合列表 = [
        {
            "名称": "保守策略",
            "策略参数": {
                "leverage": 20,
                "bid_spread": Decimal("0.003"),  # 0.3%
                "ask_spread": Decimal("0.003"),
                "position_size_ratio": Decimal("0.01"),  # 1%
            }
        },
        {
            "名称": "中等策略", 
            "策略参数": {
                "leverage": 35,
                "bid_spread": Decimal("0.002"),  # 0.2%
                "ask_spread": Decimal("0.002"),
                "position_size_ratio": Decimal("0.02"),  # 2%
            }
        },
        {
            "名称": "激进策略",
            "策略参数": {
                "leverage": 50,
                "bid_spread": Decimal("0.001"),  # 0.1%
                "ask_spread": Decimal("0.001"), 
                "position_size_ratio": Decimal("0.03"),  # 3%
            }
        }
    ]
    
    结果列表 = []
    
    for i, 参数组合 in enumerate(参数组合列表, 1):
        print(f"🔄 测试参数组合 {i}/{len(参数组合列表)}: {参数组合['名称']}")
        print(f"   杠杆: {参数组合['策略参数']['leverage']}x")
        print(f"   价差: ±{参数组合['策略参数']['bid_spread']*100:.1f}%")
        print(f"   仓位比例: {参数组合['策略参数']['position_size_ratio']*100:.1f}%")
        
        try:
            # 运行回测（第一次会预处理数据，后续使用缓存）
            结果 = run_backtest_with_params(
                strategy_params=参数组合['策略参数'],
                use_cache=True  # 使用缓存加速
            )
            
            结果['参数组合名称'] = 参数组合['名称']
            结果['参数'] = 参数组合['策略参数']
            结果列表.append(结果)
            
            print(f"   ✅ 完成 - 收益率: {结果['total_return']*100:.2f}%, 交易次数: {结果['total_trades']}")
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
        
        print()
    
    # 生成对比报告
    if 结果列表:
        print("="*70)
        print("📊 参数遍历结果对比")
        print("="*70)
        
        # 创建结果DataFrame
        df_结果 = pd.DataFrame([
            {
                "策略名称": r['参数组合名称'],
                "杠杆": r['参数']['leverage'],
                "价差(%)": f"{r['参数']['bid_spread']*100:.1f}",
                "仓位比例(%)": f"{r['参数']['position_size_ratio']*100:.1f}",
                "最终权益(USDT)": f"{r['final_equity']:,.2f}",
                "总收益率(%)": f"{r['total_return']*100:.2f}",
                "交易次数": r['total_trades'],
                "手续费(USDT)": f"{r['total_fees']:.2f}",
                "是否爆仓": "是" if r['liquidated'] else "否",
                "风险退场": "是" if r['stopped_by_risk'] else "否"
            }
            for r in 结果列表
        ])
        
        print(df_结果.to_string(index=False))
        
        # 找出最佳策略
        最佳策略 = max(结果列表, key=lambda x: x['total_return'])
        print(f"\n🏆 最佳策略: {最佳策略['参数组合名称']}")
        print(f"   收益率: {最佳策略['total_return']*100:.2f}%")
        print(f"   最终权益: {最佳策略['final_equity']:,.2f} USDT")
        
        # 保存结果
        df_结果.to_csv("参数遍历结果.csv", index=False, encoding='utf-8-sig')
        print(f"\n💾 结果已保存到: 参数遍历结果.csv")

if __name__ == "__main__":
    参数遍历回测()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的2020年测试 - 验证时间范围是否正确
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest_kline_trajectory import run_backtest_with_params

def test_2020_time_range():
    """测试2020年时间范围是否正确"""
    print("🧪 测试2020年时间范围")
    print("="*50)
    
    print("📅 测试参数:")
    print("  - 开始时间: 2020-01-01")
    print("  - 结束时间: 2020-12-31")
    print("  - 杠杆: 5x")
    print()
    
    try:
        # 运行2020年回测
        results = run_backtest_with_params(
            strategy_params={
                "leverage": 5,
                "start_date": "2020-01-01",
                "end_date": "2020-12-31"
            },
            use_cache=True
        )
        
        if results:
            print("✅ 回测完成!")
            print(f"💰 最终权益: {results.get('final_equity', 0):.2f} USDT")
            print(f"📈 总收益率: {results.get('total_return', 0)*100:.2f}%")
            print(f"💥 是否爆仓: {'是' if results.get('liquidated', False) else '否'}")
            
            if results.get('liquidated', False):
                print(f"📅 爆仓时间: {results.get('liquidation_date', 'N/A')}")
            else:
                print("🎉 成功穿越2020年全年！")
        else:
            print("❌ 回测失败")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_2020_time_range()

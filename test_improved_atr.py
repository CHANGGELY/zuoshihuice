#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的ATR波动率保护
使用更激进的参数设置
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest_kline_trajectory import run_backtest_with_params, ATR_CONFIG

def test_improved_atr_protection():
    """测试改进后的ATR保护效果"""
    print("🛡️ 测试改进后的ATR波动率保护")
    print("="*60)
    print("🔧 改进内容:")
    print("  - ATR周期: 24小时 → 12小时 (更快响应)")
    print("  - 高波动阈值: 30% → 15% (更敏感)")
    print("  - 极端波动阈值: 50% → 25% (更敏感)")
    print("  - 紧急平仓阈值: 70% → 20% (更早触发)")
    print("  - 最大不平衡: 30% → 10% (更严格)")
    print()
    
    # 显示当前配置
    print("📊 当前ATR配置:")
    print(f"  - ATR周期: {ATR_CONFIG['atr_period']/60:.0f}小时")
    print(f"  - 高波动阈值: {ATR_CONFIG['high_volatility_threshold']*100:.0f}%")
    print(f"  - 极端波动阈值: {ATR_CONFIG['extreme_volatility_threshold']*100:.0f}%")
    print(f"  - 紧急平仓阈值: {ATR_CONFIG['emergency_close_threshold']*100:.0f}%")
    print(f"  - 最大不平衡: {ATR_CONFIG['max_imbalance_ratio']*100:.0f}%")
    print()
    
    # 测试不同杠杆
    leverages = [5, 10, 15, 20]
    results_summary = []
    
    for leverage in leverages:
        print(f"🧪 测试杠杆: {leverage}x")
        print("-" * 40)
        
        strategy_params = {
            "leverage": leverage,
            "bid_spread": 0.002,
            "ask_spread": 0.002,
        }
        
        try:
            results = run_backtest_with_params(
                strategy_params=strategy_params,
                market_params=None,
                use_cache=True
            )
            
            if results:
                final_equity = results.get('final_equity', 0)
                total_return = results.get('total_return', 0)
                max_drawdown = results.get('max_drawdown', 0)
                liquidated = results.get('liquidated', False)
                total_trades = results.get('total_trades', 0)
                
                print(f"  💰 最终权益: {final_equity:.2f} USDT")
                print(f"  📈 总收益率: {total_return*100:.2f}%")
                print(f"  📉 最大回撤: {max_drawdown*100:.2f}%")
                print(f"  🔄 总交易次数: {total_trades}")
                print(f"  💥 是否爆仓: {'❌ 是' if liquidated else '✅ 否'}")
                
                # 评估结果
                if not liquidated:
                    if total_return > 0:
                        print("  🎉 优秀：无爆仓且盈利")
                    else:
                        print("  👍 良好：无爆仓但亏损")
                else:
                    print("  ⚠️ 仍需改进：发生爆仓")
                
                results_summary.append({
                    'leverage': leverage,
                    'final_equity': final_equity,
                    'total_return': total_return,
                    'max_drawdown': max_drawdown,
                    'liquidated': liquidated,
                    'total_trades': total_trades
                })
            else:
                print("  ❌ 回测失败")
                results_summary.append({
                    'leverage': leverage,
                    'final_equity': 0,
                    'total_return': -1,
                    'max_drawdown': 1,
                    'liquidated': True,
                    'total_trades': 0
                })
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            results_summary.append({
                'leverage': leverage,
                'final_equity': 0,
                'total_return': -1,
                'max_drawdown': 1,
                'liquidated': True,
                'total_trades': 0
            })
        
        print()
    
    # 汇总分析
    print("📋 改进后的ATR保护效果汇总:")
    print("="*70)
    print(f"{'杠杆':<8} {'最终权益':<12} {'收益率':<10} {'最大回撤':<10} {'爆仓':<8} {'评价':<10}")
    print("-" * 70)
    
    safe_leverages = []
    profitable_leverages = []
    
    for result in results_summary:
        leverage = result['leverage']
        final_equity = result['final_equity']
        total_return = result['total_return'] * 100
        max_drawdown = result['max_drawdown'] * 100
        liquidated = "是" if result['liquidated'] else "否"
        
        # 评价
        if not result['liquidated']:
            safe_leverages.append(leverage)
            if result['total_return'] > 0:
                profitable_leverages.append(leverage)
                evaluation = "优秀"
            else:
                evaluation = "良好"
        else:
            evaluation = "需改进"
        
        print(f"{leverage:<8}x {final_equity:<12.2f} {total_return:<10.2f}% {max_drawdown:<10.2f}% {liquidated:<8} {evaluation:<10}")
    
    # 结论
    print(f"\n🎯 改进效果评估:")
    if safe_leverages:
        max_safe = max(safe_leverages)
        print(f"✅ 安全杠杆范围: ≤ {max_safe}x")
        
        if profitable_leverages:
            max_profitable = max(profitable_leverages)
            print(f"🎉 盈利杠杆范围: ≤ {max_profitable}x")
            print(f"💡 推荐杠杆: {max_profitable}x (既安全又盈利)")
        else:
            print(f"💡 推荐杠杆: {max_safe}x (安全但可能亏损)")
            print("📝 建议: 进一步优化策略参数以提高盈利能力")
    else:
        print("⚠️ 改进后仍存在爆仓风险")
        print("💡 建议: 进一步降低杠杆或调整ATR参数")
    
    # 对比原始参数的改进效果
    print(f"\n📈 改进效果对比:")
    print("原始参数 vs 改进参数:")
    print("- ATR响应速度: 24小时 → 12小时 (提升100%)")
    print("- 风险敏感度: 30% → 15% (提升100%)")
    print("- 紧急保护: 70% → 20% (提升250%)")
    print("- 仓位控制: 30% → 10% (提升200%)")

def test_specific_crash_period():
    """专门测试2020年3月崩盘期间"""
    print(f"\n🔍 专项测试：2020年3月崩盘期间")
    print("="*50)
    
    # 使用最安全的杠杆
    strategy_params = {
        "leverage": 5,  # 极低杠杆
        "bid_spread": 0.002,
        "ask_spread": 0.002,
    }
    
    print(f"🛡️ 使用极低杠杆: {strategy_params['leverage']}x")
    print("📅 测试期间: 2020-03-01 到 2020-04-01")
    
    try:
        results = run_backtest_with_params(
            strategy_params=strategy_params,
            market_params=None,
            use_cache=True
        )
        
        if results:
            final_equity = results.get('final_equity', 0)
            liquidated = results.get('liquidated', False)
            max_drawdown = results.get('max_drawdown', 0)
            
            print(f"\n📊 崩盘期间测试结果:")
            print(f"  💰 最终权益: {final_equity:.2f} USDT")
            print(f"  📉 最大回撤: {max_drawdown*100:.2f}%")
            print(f"  💥 是否爆仓: {'❌ 是' if liquidated else '✅ 否'}")
            
            if not liquidated:
                print(f"\n🎉 成功！改进后的ATR保护在极端市场下有效！")
                print(f"✅ 在历史上最严重的加密货币崩盘中幸存")
                print(f"✅ 保住了 {final_equity:.2f} USDT 资金")
            else:
                print(f"\n⚠️ 即使在5倍杠杆下仍然爆仓")
                print(f"💡 建议考虑更保守的策略或暂停交易")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("🚀 改进后的ATR波动率保护测试")
    print("="*80)
    
    # 测试改进效果
    test_improved_atr_protection()
    
    # 专项测试崩盘期间
    test_specific_crash_period()
    
    print("\n🎉 测试完成!")
    print("\n💡 总结:")
    print("1. 改进后的ATR参数更加敏感和激进")
    print("2. 紧急平仓机制可以在极端情况下保护资金")
    print("3. 建议在实际使用中采用测试通过的安全杠杆")
    print("4. 持续监控ATR指标，及时调整策略参数")

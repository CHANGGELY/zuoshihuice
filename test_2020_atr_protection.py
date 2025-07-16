#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2020年ATR波动率保护效果测试
专门测试2020年全年数据，包含3月崩盘期间的表现
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest_kline_trajectory import run_backtest_with_params, ATR_CONFIG

def test_2020_atr_protection():
    """测试2020年ATR保护效果"""
    print("🚀 2020年ATR波动率保护效果测试")
    print("="*80)
    print("📅 测试时间段: 2020年1月1日 - 2020年12月31日")
    print("🎯 关键测试点:")
    print("  - 2020年3月12-13日: 史上最大单日跌幅 (-50%)")
    print("  - 2020年3月整月: 持续暴跌和反弹")
    print("  - 2020年下半年: 牛市启动期")
    print("  - 全年波动: ETH从$130涨到$730")
    print()
    
    # 显示当前配置
    print("📊 当前ATR配置:")
    print(f"  - ATR周期: {ATR_CONFIG['atr_period']/60:.0f}小时")
    print(f"  - 高波动阈值: {ATR_CONFIG['high_volatility_threshold']*100:.0f}%")
    print(f"  - 极端波动阈值: {ATR_CONFIG['extreme_volatility_threshold']*100:.0f}%")
    print(f"  - 紧急平仓阈值: {ATR_CONFIG['emergency_close_threshold']*100:.0f}%")
    print()
    
    # 测试不同杠杆水平
    leverage_tests = [5, 10, 15, 20, 25]
    
    print("🧪 测试不同杠杆水平在2020年的表现:")
    print("="*60)
    
    results_summary = []
    
    for leverage in leverage_tests:
        print(f"\n📊 测试杠杆: {leverage}x")
        print("-" * 40)
        
        try:
            # 运行2020年全年回测
            results = run_backtest_with_params(
                strategy_params={
                    "leverage": leverage,
                    "bid_spread": 0.002,
                    "ask_spread": 0.002,
                    "start_date": "2020-01-01",
                    "end_date": "2020-12-31"
                },
                market_params=None,
                use_cache=True
            )
            
            if results:
                final_equity = results.get('final_equity', 0)
                total_return = results.get('total_return', 0)
                max_drawdown = results.get('max_drawdown', 0)
                liquidated = results.get('liquidated', False)
                total_trades = results.get('total_trades', 0)
                liquidation_date = results.get('liquidation_date', None)
                
                print(f"  💰 最终权益: {final_equity:.2f} USDT")
                print(f"  📈 总收益率: {total_return*100:.2f}%")
                print(f"  📉 最大回撤: {max_drawdown*100:.2f}%")
                print(f"  🔄 总交易次数: {total_trades}")
                print(f"  💥 是否爆仓: {'❌ 是' if liquidated else '✅ 否'}")
                if liquidated and liquidation_date:
                    print(f"  📅 爆仓时间: {liquidation_date}")
                
                # 评估结果
                if not liquidated:
                    if total_return > 0:
                        evaluation = "🎉 优秀"
                        print(f"  {evaluation}: 无爆仓且盈利，ATR保护有效！")
                    elif total_return > -0.3:
                        evaluation = "👍 良好"
                        print(f"  {evaluation}: 无爆仓，轻微亏损，保护有效")
                    else:
                        evaluation = "⚠️ 一般"
                        print(f"  {evaluation}: 无爆仓但亏损较大")
                else:
                    evaluation = "❌ 失败"
                    print(f"  {evaluation}: 发生爆仓，需要调整参数")
                
                results_summary.append({
                    'leverage': leverage,
                    'final_equity': final_equity,
                    'total_return': total_return,
                    'max_drawdown': max_drawdown,
                    'liquidated': liquidated,
                    'total_trades': total_trades,
                    'evaluation': evaluation,
                    'liquidation_date': liquidation_date
                })
            else:
                print(f"  ❌ 回测失败")
                results_summary.append({
                    'leverage': leverage,
                    'final_equity': 0,
                    'total_return': -1,
                    'max_drawdown': 1,
                    'liquidated': True,
                    'total_trades': 0,
                    'evaluation': "❌ 失败",
                    'liquidation_date': None
                })
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            results_summary.append({
                'leverage': leverage,
                'final_equity': 0,
                'total_return': -1,
                'max_drawdown': 1,
                'liquidated': True,
                'total_trades': 0,
                'evaluation': "❌ 错误",
                'liquidation_date': None
            })
    
    # 汇总分析
    print(f"\n📋 2020年杠杆测试汇总:")
    print("="*90)
    print(f"{'杠杆':<8} {'最终权益':<12} {'收益率':<10} {'最大回撤':<10} {'交易次数':<10} {'爆仓':<8} {'评价':<10}")
    print("-" * 90)
    
    safe_leverages = []
    profitable_leverages = []
    
    for result in results_summary:
        leverage = result['leverage']
        final_equity = result['final_equity']
        total_return = result['total_return'] * 100
        max_drawdown = result['max_drawdown'] * 100
        total_trades = result['total_trades']
        liquidated = "是" if result['liquidated'] else "否"
        evaluation = result['evaluation']
        
        print(f"{leverage:<8}x {final_equity:<12.0f} {total_return:<10.1f}% {max_drawdown:<10.1f}% {total_trades:<10} {liquidated:<8} {evaluation:<10}")
        
        if not result['liquidated']:
            safe_leverages.append(leverage)
            if result['total_return'] > 0:
                profitable_leverages.append(leverage)
    
    # 结论和建议
    print(f"\n🎯 2020年测试结论:")
    print("="*50)
    
    if safe_leverages:
        max_safe = max(safe_leverages)
        print(f"✅ 安全杠杆范围: ≤ {max_safe}x")
        print(f"🛡️ ATR保护在{max_safe}倍杠杆下成功防止爆仓")
        
        if profitable_leverages:
            max_profitable = max(profitable_leverages)
            best_result = next(r for r in results_summary if r['leverage'] == max_profitable)
            print(f"🎉 最佳杠杆: {max_profitable}x")
            print(f"   - 最终权益: {best_result['final_equity']:.0f} USDT")
            print(f"   - 年化收益: {best_result['total_return']*100:.1f}%")
            print(f"   - 最大回撤: {best_result['max_drawdown']*100:.1f}%")
            print(f"   - 成功穿越2020年3月崩盘！")
        else:
            print(f"💡 推荐杠杆: {max_safe}x (安全但可能亏损)")
            print(f"📝 建议: 优化策略参数以提高盈利能力")
    else:
        print("⚠️ 所有测试杠杆都存在爆仓风险")
        print("💡 建议:")
        print("   - 进一步降低ATR阈值 (30% → 20% → 15%)")
        print("   - 启用紧急平仓机制")
        print("   - 使用更低杠杆 (3x-5x)")
    
    # 分析爆仓时间点
    liquidated_results = [r for r in results_summary if r['liquidated'] and r['liquidation_date']]
    if liquidated_results:
        print(f"\n💥 爆仓时间分析:")
        for result in liquidated_results:
            print(f"   {result['leverage']}x杠杆: {result['liquidation_date']}")
    
    return results_summary

def test_atr_parameter_sensitivity():
    """测试ATR参数敏感性"""
    print(f"\n🔬 ATR参数敏感性测试 - 2020年数据")
    print("="*60)
    
    # 测试不同ATR阈值组合
    atr_test_configs = [
        {
            "name": "当前配置",
            "high_threshold": 0.30,
            "extreme_threshold": 0.50,
            "description": "默认配置"
        },
        {
            "name": "敏感配置",
            "high_threshold": 0.20,
            "extreme_threshold": 0.35,
            "description": "更早触发保护"
        },
        {
            "name": "保守配置",
            "high_threshold": 0.15,
            "extreme_threshold": 0.25,
            "description": "极度保守"
        },
        {
            "name": "激进配置",
            "high_threshold": 0.40,
            "extreme_threshold": 0.60,
            "description": "较晚触发"
        }
    ]
    
    atr_results = []
    
    for config in atr_test_configs:
        print(f"\n📊 测试 {config['name']}")
        print(f"   高波动: {config['high_threshold']*100:.0f}%, 极端波动: {config['extreme_threshold']*100:.0f}%")
        print(f"   {config['description']}")
        
        # 备份原始配置
        original_config = ATR_CONFIG.copy()
        
        try:
            # 更新测试配置
            ATR_CONFIG.update({
                "high_volatility_threshold": config['high_threshold'],
                "extreme_volatility_threshold": config['extreme_threshold'],
            })
            
            # 使用中等杠杆测试
            results = run_backtest_with_params(
                strategy_params={
                    "leverage": 10,
                    "start_date": "2020-01-01",
                    "end_date": "2020-12-31"
                },
                market_params=None,
                use_cache=True
            )
            
            if results:
                final_equity = results.get('final_equity', 0)
                liquidated = results.get('liquidated', False)
                total_return = results.get('total_return', 0)
                max_drawdown = results.get('max_drawdown', 0)
                
                print(f"   结果: 权益 {final_equity:.0f} USDT, 收益 {total_return*100:.1f}%, 回撤 {max_drawdown*100:.1f}%, 爆仓 {'是' if liquidated else '否'}")
                
                atr_results.append({
                    'name': config['name'],
                    'final_equity': final_equity,
                    'liquidated': liquidated,
                    'total_return': total_return,
                    'max_drawdown': max_drawdown
                })
            else:
                print(f"   结果: 测试失败")
                atr_results.append({
                    'name': config['name'],
                    'final_equity': 0,
                    'liquidated': True,
                    'total_return': -1,
                    'max_drawdown': 1
                })
                
        except Exception as e:
            print(f"   结果: 错误 - {e}")
            atr_results.append({
                'name': config['name'],
                'final_equity': 0,
                'liquidated': True,
                'total_return': -1,
                'max_drawdown': 1
            })
            
        finally:
            # 恢复原始配置
            ATR_CONFIG.clear()
            ATR_CONFIG.update(original_config)
    
    # ATR参数对比
    print(f"\n📋 ATR参数对比:")
    print("-" * 60)
    safe_configs = [r for r in atr_results if not r['liquidated']]
    if safe_configs:
        best_config = max(safe_configs, key=lambda x: x['total_return'])
        print(f"🏆 最佳ATR配置: {best_config['name']}")
        print(f"   最终权益: {best_config['final_equity']:.0f} USDT")
        print(f"   总收益率: {best_config['total_return']*100:.1f}%")
        print(f"   最大回撤: {best_config['max_drawdown']*100:.1f}%")
    else:
        print("⚠️ 所有ATR配置都存在爆仓风险")

if __name__ == "__main__":
    print("🚀 2020年ATR波动率保护全面测试")
    print("="*80)
    
    # 主要测试：不同杠杆的表现
    leverage_results = test_2020_atr_protection()
    
    # 参数敏感性测试
    test_atr_parameter_sensitivity()
    
    print("\n🎉 2020年测试完成!")
    print("\n💡 关键结论:")
    print("1. 如果有杠杆能在2020年3月崩盘中幸存，说明ATR保护有效")
    print("2. 最佳杠杆应该既能防爆仓，又能获得合理收益")
    print("3. ATR参数需要在保护效果和收益之间找到平衡")
    print("4. 2020年是极端测试案例，通过此测试的配置相对安全")
    
    # 给出最终建议
    safe_results = [r for r in leverage_results if not r['liquidated']]
    if safe_results:
        best_leverage = max(safe_results, key=lambda x: x['total_return'])['leverage']
        print(f"\n🎯 最终建议:")
        print(f"   推荐杠杆: {best_leverage}x")
        print(f"   当前ATR配置在此杠杆下表现良好")
        print(f"   可以考虑在实盘中使用此配置")
    else:
        print(f"\n⚠️ 需要进一步优化:")
        print(f"   建议降低ATR阈值或使用更低杠杆")
        print(f"   2020年3月的极端波动需要更保守的参数")

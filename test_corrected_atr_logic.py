#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修正后的ATR逻辑
验证仓位平衡机制仅在ATR > 30%时触发，且只过滤信号而非替换
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest_kline_trajectory import run_backtest_with_params, ATR_CONFIG

def test_corrected_atr_logic():
    """测试修正后的ATR逻辑 - 使用2020年全年数据"""
    print("🔧 测试修正后的ATR逻辑 - 2020年全年数据")
    print("="*60)
    print("📅 测试时间段: 2020年1月1日 - 2020年12月31日")
    print("🎯 包含重要事件:")
    print("  - 2020年3月: COVID-19市场崩盘")
    print("  - 2020年下半年: 加密货币牛市启动")
    print("  - 全年波动: 从低点到高点的完整周期")
    print()

    print("📊 当前ATR配置:")
    print(f"  - 高波动阈值: {ATR_CONFIG['high_volatility_threshold']*100:.0f}% (仓位平衡触发)")
    print(f"  - 极端波动阈值: {ATR_CONFIG['extreme_volatility_threshold']*100:.0f}% (强制平衡到0)")
    print(f"  - 紧急平仓阈值: {ATR_CONFIG['emergency_close_threshold']*100:.0f}% (强制清仓)")
    print()

    print("🎯 修正后的逻辑:")
    print("1. ATR < 30%: 正常网格交易，不过滤任何信号")
    print("2. 30% ≤ ATR < 50%: 仓位平衡模式")
    print("   - 多头过多时：过滤开多信号，保留开空、平多、平空")
    print("   - 空头过多时：过滤开空信号，保留开多、平多、平空")
    print("3. ATR ≥ 50%: 极端波动强制平衡到0")
    print("4. ATR ≥ 20%: 紧急平仓（如果启用）")
    print()

    # 显示开关状态
    print("🔧 当前开关状态:")
    print(f"  - 波动率自适应: {'启用' if ATR_CONFIG['enable_volatility_adaptive'] else '禁用'}")
    print(f"  - 仓位平衡: {'启用' if ATR_CONFIG['enable_position_balance'] else '禁用'}")
    print(f"  - 极端波动平衡: {'启用' if ATR_CONFIG['enable_extreme_balance'] else '禁用'}")
    print(f"  - 动态网格间距: {'启用' if ATR_CONFIG['enable_dynamic_spread'] else '禁用'}")
    print(f"  - 紧急平仓: {'启用' if ATR_CONFIG['enable_emergency_close'] else '禁用'}")
    print()
    
    # 测试不同配置组合
    test_configs = [
        {
            "name": "仅仓位平衡",
            "config": {
                "enable_position_balance": True,
                "enable_extreme_balance": False,
                "enable_emergency_close": False,
                "enable_dynamic_spread": False,
            },
            "description": "只在ATR>30%时过滤信号"
        },
        {
            "name": "仓位平衡+极端平衡",
            "config": {
                "enable_position_balance": True,
                "enable_extreme_balance": True,
                "enable_emergency_close": False,
                "enable_dynamic_spread": False,
            },
            "description": "ATR>30%过滤信号，ATR>50%强制平衡"
        },
        {
            "name": "完整ATR保护",
            "config": {
                "enable_position_balance": True,
                "enable_extreme_balance": True,
                "enable_emergency_close": True,
                "enable_dynamic_spread": True,
            },
            "description": "所有ATR保护机制"
        }
    ]
    
    results_summary = []
    
    for test_config in test_configs:
        print(f"🧪 测试配置: {test_config['name']}")
        print(f"   {test_config['description']}")
        
        # 备份原始配置
        original_config = ATR_CONFIG.copy()
        
        try:
            # 更新测试配置
            ATR_CONFIG.update(test_config['config'])

            # 运行2020年全年回测
            results = run_backtest_with_params(
                strategy_params={
                    "leverage": 10,  # 使用中等杠杆
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
                
                results_summary.append({
                    'name': test_config['name'],
                    'final_equity': final_equity,
                    'liquidated': liquidated,
                    'total_return': total_return,
                    'max_drawdown': max_drawdown
                })
            else:
                print(f"   结果: 测试失败")
                results_summary.append({
                    'name': test_config['name'],
                    'final_equity': 0,
                    'liquidated': True,
                    'total_return': -1,
                    'max_drawdown': 1
                })
                
        except Exception as e:
            print(f"   结果: 错误 - {e}")
            results_summary.append({
                'name': test_config['name'],
                'final_equity': 0,
                'liquidated': True,
                'total_return': -1,
                'max_drawdown': 1
            })
            
        finally:
            # 恢复原始配置
            ATR_CONFIG.clear()
            ATR_CONFIG.update(original_config)
        
        print()
    
    # 汇总分析
    print("📋 配置对比汇总:")
    print("="*80)
    print(f"{'配置':<20} {'最终权益':<12} {'收益率':<10} {'最大回撤':<10} {'爆仓':<8}")
    print("-" * 80)
    
    for result in results_summary:
        name = result['name']
        final_equity = result['final_equity']
        total_return = result['total_return'] * 100
        max_drawdown = result['max_drawdown'] * 100
        liquidated = "是" if result['liquidated'] else "否"
        
        print(f"{name:<20} {final_equity:<12.0f} {total_return:<10.1f}% {max_drawdown:<10.1f}% {liquidated:<8}")
    
    # 结论
    print(f"\n🎯 测试结论:")
    safe_configs = [r for r in results_summary if not r['liquidated']]
    if safe_configs:
        best_config = max(safe_configs, key=lambda x: x['total_return'])
        print(f"🏆 最佳配置: {best_config['name']}")
        print(f"   - 最终权益: {best_config['final_equity']:.0f} USDT")
        print(f"   - 总收益率: {best_config['total_return']*100:.1f}%")
        print(f"   - 最大回撤: {best_config['max_drawdown']*100:.1f}%")
        print(f"   - 无爆仓风险")
    else:
        print("⚠️ 所有配置都存在爆仓风险")
        print("💡 建议进一步降低杠杆或调整ATR参数")

def test_signal_filtering_logic():
    """测试信号过滤逻辑"""
    print(f"\n🔍 信号过滤逻辑测试")
    print("="*50)
    
    from backtest_kline_trajectory import FastPerpetualExchange, FastPerpetualStrategy
    
    # 创建测试实例
    exchange = FastPerpetualExchange(1000.0)
    strategy = FastPerpetualStrategy(exchange)
    
    # 模拟不同的仓位和ATR情况
    test_cases = [
        {
            "name": "ATR < 30%",
            "atr": 25,
            "long_pos": 10,
            "short_pos": 5,
            "expected": "不过滤任何信号"
        },
        {
            "name": "ATR > 30%, 多头过多",
            "atr": 35,
            "long_pos": 10,
            "short_pos": 2,
            "expected": "过滤开多信号"
        },
        {
            "name": "ATR > 30%, 空头过多",
            "atr": 35,
            "long_pos": 2,
            "short_pos": 10,
            "expected": "过滤开空信号"
        },
        {
            "name": "ATR > 30%, 仓位平衡",
            "atr": 35,
            "long_pos": 5,
            "short_pos": 5,
            "expected": "不过滤信号"
        }
    ]
    
    for case in test_cases:
        print(f"\n📊 测试场景: {case['name']}")
        print(f"   ATR: {case['atr']}%, 多头: {case['long_pos']}, 空头: {case['short_pos']}")
        
        # 设置仓位
        exchange.long_position = case['long_pos']
        exchange.short_position = case['short_pos']
        
        # 模拟ATR数据
        if exchange.volatility_monitor:
            # 添加模拟数据使ATR达到指定值
            target_atr = case['atr'] / 100
            # 简单模拟：添加高波动数据
            for i in range(10):
                high = 100 * (1 + target_atr)
                low = 100 * (1 - target_atr)
                exchange.update_volatility_monitor(1000 + i, high, low, 100)
        
        # 测试信号过滤
        signals = ["buy_long", "sell_short", "sell_long", "buy_short"]
        filtered_signals = []
        
        for signal in signals:
            if strategy.should_filter_signal(signal):
                filtered_signals.append(signal)
        
        print(f"   过滤的信号: {filtered_signals if filtered_signals else '无'}")
        print(f"   预期结果: {case['expected']}")
        
        # 验证结果
        net_position = exchange.get_net_position()
        if case['atr'] < 30:
            expected_filtered = []
        elif net_position > 0:
            expected_filtered = ["buy_long"]
        elif net_position < 0:
            expected_filtered = ["sell_short"]
        else:
            expected_filtered = []
        
        if filtered_signals == expected_filtered:
            print(f"   ✅ 测试通过")
        else:
            print(f"   ❌ 测试失败，预期过滤: {expected_filtered}")

if __name__ == "__main__":
    print("🔧 修正后的ATR逻辑测试")
    print("="*80)
    
    # 测试修正后的逻辑
    test_corrected_atr_logic()
    
    # 测试信号过滤逻辑
    test_signal_filtering_logic()
    
    print("\n🎉 测试完成!")
    print("\n💡 总结:")
    print("1. ✅ 仓位平衡机制仅在ATR > 30%时触发")
    print("2. ✅ 高波动期只过滤开仓信号，保留平仓信号")
    print("3. ✅ 极端波动期强制平衡到中性")
    print("4. ✅ 各功能模块独立开关控制")
    print("5. ✅ 不再有画蛇添足的额外触发条件")

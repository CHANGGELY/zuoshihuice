#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义ATR参数运行回测
方便快速调整和测试不同的ATR参数组合
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入回测引擎和配置
from backtest_kline_trajectory import run_backtest_with_params, ATR_CONFIG

def run_custom_atr_backtest():
    """使用自定义ATR参数运行回测"""
    
    print("🚀 自定义ATR参数回测")
    print("="*60)
    
    # =====================================================================================
    # 🎯 在这里修改你的ATR参数 - 方便快速调整
    # =====================================================================================
    
    # 🌊 ATR波动率参数 - 你可以在这里快速调整
    custom_atr_params = {
        "enable_volatility_adaptive": True,    # 是否启用ATR保护
        "atr_period": 12 * 60,                # ATR计算周期 (小时*60)
        "high_volatility_threshold": 0.15,    # 高波动阈值 (15% = 0.15)
        "extreme_volatility_threshold": 0.25, # 极端波动阈值 (25% = 0.25)
        "emergency_close_threshold": 0.20,    # 紧急平仓阈值 (20% = 0.20)
        "max_imbalance_ratio": 0.1,           # 最大仓位不平衡 (10% = 0.1)
        "position_balance_ratio": 0.5,        # 仓位平衡目标比例
    }
    
    # 📊 策略参数 - 你可以在这里调整杠杆和价差
    strategy_params = {
        "leverage": 5,                         # 杠杆倍数
        "bid_spread": 0.002,                  # 买单价差 (0.2% = 0.002)
        "ask_spread": 0.002,                  # 卖单价差 (0.2% = 0.002)
    }
    
    # 📅 回测时间范围 - 2020年全年数据
    backtest_params = {
        "start_date": "2020-01-01",           # 开始日期 (2020年全年)
        "end_date": "2020-12-31",             # 结束日期
        "initial_balance": 1000,              # 初始资金
        "plot_equity_curve": True,            # 是否绘制资金曲线
    }
    
    # =====================================================================================
    # 显示当前配置
    # =====================================================================================
    
    print("📊 当前ATR配置:")
    print(f"  - 启用ATR保护: {'是' if custom_atr_params['enable_volatility_adaptive'] else '否'}")
    print(f"  - ATR周期: {custom_atr_params['atr_period']/60:.0f}小时")
    print(f"  - 高波动阈值: {custom_atr_params['high_volatility_threshold']*100:.0f}%")
    print(f"  - 极端波动阈值: {custom_atr_params['extreme_volatility_threshold']*100:.0f}%")
    print(f"  - 紧急平仓阈值: {custom_atr_params['emergency_close_threshold']*100:.0f}%")
    print(f"  - 最大仓位不平衡: {custom_atr_params['max_imbalance_ratio']*100:.0f}%")
    print()
    
    print("📊 当前策略配置:")
    print(f"  - 杠杆倍数: {strategy_params['leverage']}x")
    print(f"  - 买单价差: {strategy_params['bid_spread']*100:.2f}%")
    print(f"  - 卖单价差: {strategy_params['ask_spread']*100:.2f}%")
    print()
    
    print("📅 回测时间范围:")
    print(f"  - 开始日期: {backtest_params['start_date']}")
    print(f"  - 结束日期: {backtest_params['end_date']}")
    print(f"  - 测试周期: 2020年全年 (包含3月崩盘)")
    print(f"  - 初始资金: {backtest_params['initial_balance']} USDT")
    print()
    
    # =====================================================================================
    # 临时更新ATR配置并运行回测
    # =====================================================================================
    
    # 备份原始配置
    original_config = ATR_CONFIG.copy()
    
    try:
        # 临时更新ATR配置
        ATR_CONFIG.update(custom_atr_params)
        
        print("🚀 开始回测...")
        print("-" * 60)
        
        # 运行回测
        results = run_backtest_with_params(
            strategy_params=strategy_params,
            market_params=None,
            use_cache=True
        )
        
        # 显示结果
        print("\n📊 回测结果:")
        print("="*50)
        
        if results:
            final_equity = results.get('final_equity', 0)
            total_return = results.get('total_return', 0)
            max_drawdown = results.get('max_drawdown', 0)
            liquidated = results.get('liquidated', False)
            total_trades = results.get('total_trades', 0)
            
            print(f"💰 最终权益: {final_equity:.2f} USDT")
            print(f"📈 总收益率: {total_return*100:.2f}%")
            print(f"📉 最大回撤: {max_drawdown*100:.2f}%")
            print(f"🔄 总交易次数: {total_trades}")
            print(f"💥 是否爆仓: {'❌ 是' if liquidated else '✅ 否'}")
            
            # 评估结果
            print(f"\n🎯 结果评估:")
            if not liquidated:
                if total_return > 0:
                    print("🎉 优秀：无爆仓且盈利！")
                    print("✅ ATR保护机制有效，策略参数合适")
                elif total_return > -0.5:  # 亏损小于50%
                    print("👍 良好：无爆仓，轻微亏损")
                    print("✅ ATR保护机制有效，可考虑优化策略参数")
                else:
                    print("⚠️ 一般：无爆仓但亏损较大")
                    print("💡 建议调整策略参数或降低杠杆")
            else:
                print("❌ 需要改进：发生爆仓")
                print("💡 建议：")
                print("   - 降低杠杆倍数")
                print("   - 降低ATR阈值（更敏感）")
                print("   - 降低紧急平仓阈值")
                
        else:
            print("❌ 回测失败，无法获取结果")
            
    except Exception as e:
        print(f"❌ 回测过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 恢复原始配置
        ATR_CONFIG.clear()
        ATR_CONFIG.update(original_config)
        print(f"\n✅ ATR配置已恢复为原始设置")

def quick_parameter_test():
    """快速测试多组参数"""
    print("\n🧪 快速参数测试")
    print("="*60)
    
    # 定义多组测试参数
    test_cases = [
        {
            "name": "保守型",
            "atr_threshold": 0.10,  # 10%
            "emergency_threshold": 0.15,  # 15%
            "leverage": 3,
            "description": "极低风险，适合新手"
        },
        {
            "name": "平衡型", 
            "atr_threshold": 0.15,  # 15%
            "emergency_threshold": 0.20,  # 20%
            "leverage": 5,
            "description": "平衡风险收益"
        },
        {
            "name": "激进型",
            "atr_threshold": 0.20,  # 20%
            "emergency_threshold": 0.25,  # 25%
            "leverage": 10,
            "description": "高风险高收益"
        }
    ]
    
    results_summary = []
    
    for test_case in test_cases:
        print(f"\n📊 测试 {test_case['name']} 参数组合")
        print(f"   {test_case['description']}")
        print(f"   ATR阈值: {test_case['atr_threshold']*100:.0f}%, 紧急阈值: {test_case['emergency_threshold']*100:.0f}%, 杠杆: {test_case['leverage']}x")
        
        # 备份原始配置
        original_config = ATR_CONFIG.copy()
        
        try:
            # 更新测试配置
            ATR_CONFIG.update({
                "high_volatility_threshold": test_case['atr_threshold'],
                "emergency_close_threshold": test_case['emergency_threshold'],
            })
            
            # 运行2020年全年回测
            results = run_backtest_with_params(
                strategy_params={
                    "leverage": test_case['leverage'],
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
                
                print(f"   结果: 权益 {final_equity:.0f} USDT, 收益 {total_return*100:.1f}%, 爆仓 {'是' if liquidated else '否'}")
                
                results_summary.append({
                    'name': test_case['name'],
                    'final_equity': final_equity,
                    'liquidated': liquidated,
                    'total_return': total_return
                })
            else:
                print(f"   结果: 测试失败")
                results_summary.append({
                    'name': test_case['name'],
                    'final_equity': 0,
                    'liquidated': True,
                    'total_return': -1
                })
                
        except Exception as e:
            print(f"   结果: 错误 - {e}")
            results_summary.append({
                'name': test_case['name'],
                'final_equity': 0,
                'liquidated': True,
                'total_return': -1
            })
            
        finally:
            # 恢复原始配置
            ATR_CONFIG.clear()
            ATR_CONFIG.update(original_config)
    
    # 汇总结果
    print(f"\n📋 参数测试汇总:")
    print("-" * 40)
    safe_configs = [r for r in results_summary if not r['liquidated']]
    if safe_configs:
        best_config = max(safe_configs, key=lambda x: x['total_return'])
        print(f"🏆 推荐配置: {best_config['name']}")
        print(f"   最终权益: {best_config['final_equity']:.0f} USDT")
        print(f"   总收益率: {best_config['total_return']*100:.1f}%")
    else:
        print("⚠️ 所有配置都存在爆仓风险，建议进一步降低参数")

if __name__ == "__main__":
    print("🎯 ATR参数自定义回测工具")
    print("="*80)
    print("💡 使用说明:")
    print("1. 修改脚本顶部的 custom_atr_params 来调整ATR参数")
    print("2. 修改 strategy_params 来调整策略参数")
    print("3. 修改 backtest_params 来调整回测时间范围")
    print("4. 运行脚本查看结果")
    print()
    
    # 运行自定义参数回测
    run_custom_atr_backtest()
    
    # 运行快速参数测试
    quick_parameter_test()
    
    print("\n🎉 测试完成!")
    print("\n💡 下次调整参数时，直接修改脚本顶部的参数即可！")

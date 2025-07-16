# 🌊 ATR波动率自适应 - 简化配置说明

## 📊 核心参数 (backtest_kline_trajectory.py 顶部)

```python
ATR_CONFIG = {
    # 🔧 主开关
    "enable_volatility_adaptive": True,    # 启用波动率自适应机制
    
    # 📊 ATR计算
    "atr_period": 12 * 60,                # ATR周期 (12小时)
    
    # 🚨 波动率阈值
    "high_volatility_threshold": 0.3,     # 30% - 启动仓位平衡
    "extreme_volatility_threshold": 0.5,  # 50% - 强制平衡到0
    
    # 🎯 功能开关
    "enable_position_balance": True,       # 仓位平衡机制
    "enable_extreme_balance": True,        # 极端波动强制平衡
    "enable_dynamic_spread": False,        # 动态网格间距
    "enable_emergency_close": False,       # 紧急平仓机制
    
    # 📏 动态网格参数 (如果启用)
    "base_spread": 0.002,                 # 基础价差 0.2%
    "max_spread_multiplier": 5.0,         # 极端波动倍数
    "spread_adjustment_factor": 3.0,      # 高波动倍数
    
    # 🚨 紧急平仓参数 (如果启用)
    "emergency_close_threshold": 0.20,    # 20% - 强制清仓
    
    # ⚙️ 其他
    "gradual_adjustment": False,          # 渐进式调整
}
```

## 🎯 工作逻辑

### 1. ATR < 30%
- **状态**: 正常网格交易
- **行为**: 不过滤任何信号，正常开多开空平多平空

### 2. 30% ≤ ATR < 50%
- **状态**: 仓位平衡模式
- **行为**: 
  - 多头过多时：过滤开多信号，保留开空、平多、平空
  - 空头过多时：过滤开空信号，保留开多、平多、平空
  - 净持仓为0时：不过滤任何信号

### 3. ATR ≥ 50% (如果启用极端平衡)
- **状态**: 极端波动强制平衡
- **行为**: 立即平掉所有净持仓，强制平衡到0

### 4. ATR ≥ 20% (如果启用紧急平仓)
- **状态**: 紧急平仓
- **行为**: 立即平掉所有多头和空头仓位

## 🔧 常用配置组合

### 保守型 (推荐新手)
```python
"high_volatility_threshold": 0.15,     # 15% - 更敏感
"extreme_volatility_threshold": 0.25,  # 25% - 更早触发
"enable_position_balance": True,
"enable_extreme_balance": True,
"enable_emergency_close": True,
"emergency_close_threshold": 0.10,     # 10% - 更早清仓
```

### 平衡型 (推荐一般用户)
```python
"high_volatility_threshold": 0.30,     # 30%
"extreme_volatility_threshold": 0.50,  # 50%
"enable_position_balance": True,
"enable_extreme_balance": True,
"enable_emergency_close": False,       # 不启用紧急平仓
```

### 激进型 (高风险用户)
```python
"high_volatility_threshold": 0.50,     # 50% - 不敏感
"extreme_volatility_threshold": 0.70,  # 70% - 很晚触发
"enable_position_balance": True,
"enable_extreme_balance": False,       # 不启用极端平衡
"enable_emergency_close": False,
```

### 仅信号过滤 (最简单)
```python
"enable_position_balance": True,       # 只启用信号过滤
"enable_extreme_balance": False,
"enable_emergency_close": False,
"enable_dynamic_spread": False,
```

## 💡 调参建议

### 🎯 如果经常爆仓
1. 降低 `high_volatility_threshold` (30% → 20%)
2. 启用 `enable_emergency_close`
3. 降低 `emergency_close_threshold` (20% → 15%)

### 📈 如果收益太低
1. 提高 `high_volatility_threshold` (30% → 40%)
2. 关闭 `enable_extreme_balance`
3. 关闭 `enable_emergency_close`

### ⚖️ 如果回撤太大
1. 启用 `enable_extreme_balance`
2. 降低 `extreme_volatility_threshold` (50% → 40%)
3. 启用 `enable_dynamic_spread`

## 🚀 快速测试

修改参数后运行：
```bash
python run_backtest_with_custom_atr.py
```

或者运行测试脚本：
```bash
python test_corrected_atr_logic.py
```

## ❓ 常见问题

**Q: 为什么删除了 position_balance_ratio 和 max_imbalance_ratio？**
A: 新逻辑更简单，只在ATR>30%时过滤信号，不需要复杂的比例计算。

**Q: 信号过滤是什么意思？**
A: 原策略继续运行，但某些开仓信号会被过滤掉，平仓信号始终保留。

**Q: 极端波动和紧急平仓有什么区别？**
A: 极端波动只平净持仓到0，紧急平仓是清空所有仓位。

**Q: 如何知道ATR保护是否生效？**
A: 运行时会打印日志，如"🔥 极端波动！ATR=55% - 强制平衡到中性"。

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步版本的回测引擎
解决Django多线程和异步函数冲突问题
完全保持原始逻辑，只是去除异步和全局状态
"""

import pandas as pd
import numpy as np
from decimal import Decimal, getcontext
from typing import Dict, List, Optional, Tuple
import pickle
import os
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置高精度计算
getcontext().prec = 50

class SyncPerpetualExchange:
    """同步版本的永续合约交易所"""
    
    def __init__(self, initial_balance: float, config: Dict):
        self.balance = Decimal(str(initial_balance))
        self.long_position = Decimal("0")
        self.short_position = Decimal("0")
        self.long_avg_price = Decimal("0")
        self.short_avg_price = Decimal("0")
        self.current_price = Decimal("0")
        self.total_fees_paid = Decimal("0")
        self.trade_history = []
        self.equity_history = []
        self.config = config
        
        # 杠杆相关
        self.current_leverage = config["leverage"]
        
    def get_equity(self) -> Decimal:
        """计算总权益"""
        return self.balance + self.get_unrealized_pnl()
    
    def get_unrealized_pnl(self) -> Decimal:
        """计算未实现盈亏"""
        if self.current_price == 0:
            return Decimal("0")
        
        long_pnl = Decimal("0")
        short_pnl = Decimal("0")
        
        if self.long_position > 0:
            long_pnl = self.long_position * (self.current_price - self.long_avg_price)
        
        if self.short_position > 0:
            short_pnl = self.short_position * (self.short_avg_price - self.current_price)
        
        return long_pnl + short_pnl
    
    def get_current_max_leverage(self) -> int:
        """根据当前净持仓价值计算最大杠杆"""
        net_position = abs(self.long_position - self.short_position)
        net_position_value = net_position * self.current_price
        
        # 币安ETHUSDC阶梯保证金表
        if net_position_value <= 50000:
            return 125
        elif net_position_value <= 250000:
            return 100
        elif net_position_value <= 1000000:
            return 50
        elif net_position_value <= 5000000:
            return 20
        elif net_position_value <= 20000000:
            return 10
        else:
            return 5
    
    def execute_trade(self, side: str, amount: Decimal, price: Decimal, timestamp: int):
        """执行交易"""
        fee = amount * price * self.config["maker_fee"]
        self.balance -= fee
        self.total_fees_paid += fee
        
        # 记录交易
        trade_record = {
            'timestamp': str(timestamp),
            'side': side,
            'amount': float(amount),
            'price': float(price),
            'fee': float(fee),
            'pnl': 0.0
        }
        
        # 执行具体交易逻辑
        if side == "buy_long":
            if self.long_position == 0:
                self.long_avg_price = price
            else:
                total_value = self.long_position * self.long_avg_price + amount * price
                self.long_position += amount
                self.long_avg_price = total_value / self.long_position
            self.long_position += amount
            
        elif side == "sell_short":
            if self.short_position == 0:
                self.short_avg_price = price
            else:
                total_value = self.short_position * self.short_avg_price + amount * price
                self.short_position += amount
                self.short_avg_price = total_value / self.short_position
            self.short_position += amount
            
        elif side == "sell_long":
            if amount >= self.long_position:
                pnl = self.long_position * (price - self.long_avg_price)
                self.balance += pnl
                trade_record['pnl'] = float(pnl)
                self.long_position = Decimal("0")
                self.long_avg_price = Decimal("0")
            else:
                pnl = amount * (price - self.long_avg_price)
                self.balance += pnl
                trade_record['pnl'] = float(pnl)
                self.long_position -= amount
                
        elif side == "buy_short":
            if amount >= self.short_position:
                pnl = self.short_position * (self.short_avg_price - price)
                self.balance += pnl
                trade_record['pnl'] = float(pnl)
                self.short_position = Decimal("0")
                self.short_avg_price = Decimal("0")
            else:
                pnl = amount * (self.short_avg_price - price)
                self.balance += pnl
                trade_record['pnl'] = float(pnl)
                self.short_position -= amount
        
        self.trade_history.append(trade_record)

class SyncPerpetualStrategy:
    """同步版本的永续合约策略"""
    
    def __init__(self, exchange: SyncPerpetualExchange, config: Dict):
        self.exchange = exchange
        self.config = config
        self.last_order_time = 0
    
    def calculate_dynamic_order_size(self, current_price: Decimal) -> Decimal:
        """计算动态下单量"""
        if not self.config["use_dynamic_order_size"]:
            return self.config["min_order_amount"]
        
        current_equity = self.exchange.get_equity()
        order_value = current_equity * self.config["position_size_ratio"]
        order_amount = order_value / current_price
        
        min_amount = max(Decimal("0.002"), current_equity / 1000 / current_price)
        max_amount = self.config["max_order_amount"]
        
        return max(min_amount, min(order_amount, max_amount))
    
    def should_place_orders(self, timestamp: int) -> bool:
        """是否应该下单"""
        return (timestamp - self.last_order_time) >= self.config["order_refresh_time"]
    
    def generate_orders(self, current_price: Decimal, timestamp: int) -> List[tuple]:
        """生成订单"""
        if not self.should_place_orders(timestamp):
            return []
        
        self.last_order_time = timestamp
        orders = []
        
        # 计算价格
        bid_spread = self.config["bid_spread"]
        ask_spread = self.config["ask_spread"]
        bid_price = current_price * (Decimal("1") - bid_spread)
        ask_price = current_price * (Decimal("1") + ask_spread)
        
        # 获取当前仓位
        long_pos = self.exchange.long_position
        short_pos = self.exchange.short_position
        
        # 计算最大仓位限制
        current_equity = self.exchange.get_equity()
        current_max_leverage = self.exchange.get_current_max_leverage()
        max_position_value_ratio = self.config["max_position_value_ratio"]
        max_position_value = current_equity * max_position_value_ratio
        max_position_amount = max_position_value / current_price
        
        # 平仓订单
        if long_pos > 0:
            close_long_amount = self.calculate_dynamic_order_size(current_price)
            close_price = ask_price * (1 + self.config["ask_spread"])
            orders.append(("sell_long", min(close_long_amount, long_pos), close_price))
        
        if short_pos > 0:
            close_short_amount = self.calculate_dynamic_order_size(current_price)
            close_price = bid_price * (1 - self.config["bid_spread"])
            orders.append(("buy_short", min(close_short_amount, short_pos), close_price))
        
        # 开仓订单
        effective_leverage = min(current_max_leverage, self.config["leverage"])
        order_amount = self.calculate_dynamic_order_size(current_price)
        
        if long_pos < max_position_amount:
            orders.append(("buy_long", order_amount, bid_price))
        
        if short_pos < max_position_amount:
            orders.append(("sell_short", order_amount, ask_price))
        
        return orders

def run_sync_backtest(params: Dict) -> Dict:
    """运行同步回测"""
    
    # 默认配置
    default_config = {
        "data_file_path": 'K线data/ETHUSDT_1m_2019-11-01_to_2025-06-15.h5',
        "start_date": '2024-06-15',
        "end_date": '2024-12-31',
        "initial_balance": 10000,
        "leverage": 5,
        "bid_spread": Decimal("0.002"),
        "ask_spread": Decimal("0.002"),
        "maker_fee": Decimal("0.0002"),
        "taker_fee": Decimal("0.0004"),
        "use_dynamic_order_size": True,
        "position_size_ratio": Decimal("0.02"),
        "min_order_amount": Decimal("0.008"),
        "max_order_amount": Decimal("99.0"),
        "max_position_value_ratio": Decimal("0.8"),
        "order_refresh_time": 300,
        "enable_position_stop_loss": False,
        "position_stop_loss": Decimal("0.05")
    }
    
    # 更新配置
    config = default_config.copy()
    config.update(params)
    
    print(f"📊 回测配置: {config['start_date']} -> {config['end_date']}")
    print(f"💰 初始资金: {config['initial_balance']} USDT")
    print(f"⚡ 杠杆倍数: {config['leverage']}")
    
    # 加载数据
    print("📂 加载历史数据...")
    df = pd.read_hdf(config["data_file_path"], key='klines')
    
    # 筛选时间范围
    test_data = df
    if config.get("start_date"):
        start_date = pd.to_datetime(config["start_date"])
        test_data = test_data[test_data['timestamp'] >= start_date]
    if config.get("end_date"):
        end_date = pd.to_datetime(config["end_date"])
        test_data = test_data[test_data['timestamp'] < end_date]
    
    test_data = test_data.copy()
    print(f"✓ 加载了 {len(test_data)} 条K线数据")
    
    # 初始化组件
    exchange = SyncPerpetualExchange(config["initial_balance"], config)
    strategy = SyncPerpetualStrategy(exchange, config)
    
    print("🚀 开始同步回测...")
    
    # 执行回测
    for i, row in tqdm(test_data.iterrows(), total=len(test_data), desc="回测进度"):
        timestamp = int(row['timestamp'].timestamp())

        # 使用K线的5个价格点进行精确模拟
        open_price = Decimal(str(row['open']))
        high_price = Decimal(str(row['high']))
        low_price = Decimal(str(row['low']))
        close_price = Decimal(str(row['close']))

        # 5点价格轨迹：开盘 -> 高点 -> 低点 -> 收盘中间点 -> 收盘
        price_trajectory = [
            open_price,
            high_price,
            low_price,
            (low_price + close_price) / 2,
            close_price
        ]

        for price_point in price_trajectory:
            exchange.current_price = price_point

            # 生成并执行订单
            orders = strategy.generate_orders(price_point, timestamp)
            for side, amount, order_price in orders:
                # 改进的订单匹配逻辑
                should_execute = False

                if side in ["buy_long", "buy_short"]:
                    # 买单：当前价格低于或等于订单价格时成交
                    should_execute = price_point <= order_price
                elif side in ["sell_long", "sell_short"]:
                    # 卖单：当前价格高于或等于订单价格时成交
                    should_execute = price_point >= order_price

                if should_execute:
                    exchange.execute_trade(side, amount, price_point, timestamp)
        
        # 记录权益历史
        if i % 100 == 0:  # 每100个点记录一次
            exchange.equity_history.append({
                'timestamp': timestamp,
                'equity': float(exchange.get_equity())
            })
    
    # 计算结果
    final_equity = exchange.get_equity()
    initial_balance = Decimal(str(config["initial_balance"]))
    total_return = (final_equity - initial_balance) / initial_balance
    
    print("✅ 回测完成")
    print(f"📈 总收益率: {float(total_return):.4f}")
    print(f"📊 交易次数: {len(exchange.trade_history)}")
    
    return {
        'final_equity': float(final_equity),
        'total_return': float(total_return),
        'total_trades': len(exchange.trade_history),
        'total_fees': float(exchange.total_fees_paid),
        'long_position': float(exchange.long_position),
        'short_position': float(exchange.short_position),
        'liquidated': False,
        'stopped_by_risk': False,
        'start_date': config['start_date'],
        'end_date': config['end_date'],
        'trades': exchange.trade_history,
        'equity_history': exchange.equity_history
    }

if __name__ == '__main__':
    # 测试同步回测引擎
    params = {
        'start_date': '2024-06-15',
        'end_date': '2024-07-15',
        'initial_balance': 10000,
        'leverage': 5
    }
    
    result = run_sync_backtest(params)
    print("回测结果:", result)

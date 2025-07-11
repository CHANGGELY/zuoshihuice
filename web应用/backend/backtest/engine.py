"""
回测引擎 - 基于原始backtest_kline_trajectory.py
"""
import asyncio
import pandas as pd
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import logging
import numpy as np
import json
from datetime import datetime
from django.conf import settings
from pathlib import Path


class BacktestEngine:
    """永续合约做市策略回测引擎"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化配置
        self.symbol = config.get('symbol', 'ETHUSDT')
        self.start_date = config.get('start_date', '2024-06-15')
        self.end_date = config.get('end_date', '2024-07-15')
        self.initial_balance = Decimal(str(config.get('initial_balance', 1000)))
        
        # 策略配置
        self.leverage = config.get('leverage', 125)
        self.bid_spread = Decimal(str(config.get('bid_spread', 0.002)))
        self.ask_spread = Decimal(str(config.get('ask_spread', 0.002)))
        self.position_size_ratio = Decimal(str(config.get('position_size_ratio', 0.02)))
        self.max_position_value_ratio = Decimal(str(config.get('max_position_value_ratio', 0.8)))
        
        # 市场配置
        self.maker_fee = Decimal('0.0002')  # 0.02%
        self.taker_fee = Decimal('0.0005')  # 0.05%
        self.min_order_size = Decimal('0.009')
        
        # 状态变量
        self.equity = self.initial_balance
        self.long_position = Decimal('0')
        self.short_position = Decimal('0')
        self.trades = []
        self.equity_curve = []
        
        # 数据
        self.kline_data = None
        
    def load_data(self) -> bool:
        """加载K线数据"""
        try:
            # 构建数据文件路径
            data_file = settings.DATA_ROOT / f"{self.symbol}_1m_2019-11-01_to_2025-06-15.h5"
            
            if not data_file.exists():
                self.logger.error(f"数据文件不存在: {data_file}")
                return False
            
            # 加载数据
            df = pd.read_hdf(data_file, key='klines')
            
            # 转换时间
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            
            # 过滤时间范围
            df = df[(df['datetime'] >= self.start_date) & (df['datetime'] <= self.end_date)].copy()
            
            if len(df) == 0:
                self.logger.error(f"指定时间范围内无数据: {self.start_date} - {self.end_date}")
                return False
            
            self.kline_data = df.reset_index(drop=True)
            self.logger.info(f"成功加载 {len(self.kline_data)} 条K线数据")
            
            return True
            
        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")
            return False
    
    def calculate_order_size(self, price: Decimal) -> Decimal:
        """计算下单量"""
        try:
            # 基于权益比例计算
            order_value = self.equity * self.position_size_ratio
            order_size = order_value / price
            
            # 限制最小下单量
            if order_size < self.min_order_size:
                order_size = self.min_order_size
            
            return order_size.quantize(Decimal('0.001'))
            
        except Exception as e:
            self.logger.error(f"计算下单量失败: {e}")
            return self.min_order_size
    
    def check_position_limit(self, new_position_value: Decimal) -> bool:
        """检查仓位限制"""
        max_position_value = self.equity * self.max_position_value_ratio
        return new_position_value <= max_position_value
    
    def calculate_liquidation_price(self, position: Decimal, entry_price: Decimal, is_long: bool) -> Decimal:
        """计算爆仓价格"""
        try:
            if position == 0:
                return Decimal('0')
            
            # 简化的爆仓价格计算
            margin_ratio = Decimal('1') / Decimal(str(self.leverage))
            
            if is_long:
                # 多头爆仓价格
                liquidation_price = entry_price * (Decimal('1') - margin_ratio)
            else:
                # 空头爆仓价格
                liquidation_price = entry_price * (Decimal('1') + margin_ratio)
            
            return liquidation_price
            
        except Exception as e:
            self.logger.error(f"计算爆仓价格失败: {e}")
            return Decimal('0')
    
    def check_liquidation(self, current_price: Decimal) -> bool:
        """检查是否爆仓"""
        try:
            # 计算净仓位价值
            net_position = self.long_position - self.short_position
            if net_position == 0:
                return False
            
            # 计算未实现盈亏
            position_value = abs(net_position) * current_price
            
            # 简化的爆仓检查：如果权益小于仓位价值的维持保证金
            maintenance_margin = position_value / Decimal(str(self.leverage)) * Decimal('0.5')
            
            return self.equity < maintenance_margin
            
        except Exception as e:
            self.logger.error(f"爆仓检查失败: {e}")
            return False
    
    def execute_trade(self, timestamp: int, action: str, side: str, amount: Decimal, price: Decimal) -> bool:
        """执行交易"""
        try:
            # 计算手续费
            trade_value = amount * price
            fee = trade_value * self.maker_fee  # 假设都是挂单
            
            # 更新仓位
            if side == 'buy':
                if '开多' in action:
                    self.long_position += amount
                elif '平空' in action:
                    self.short_position -= amount
            else:  # sell
                if '开空' in action:
                    self.short_position += amount
                elif '平多' in action:
                    self.long_position -= amount
            
            # 更新权益（扣除手续费）
            self.equity -= fee
            
            # 记录交易
            trade_record = {
                'timestamp': timestamp,
                'action': action,
                'side': side,
                'amount': float(amount),
                'price': float(price),
                'leverage': self.leverage,
                'fee': float(fee),
                'long_position': float(self.long_position),
                'short_position': float(self.short_position),
                'net_position': float(self.long_position - self.short_position),
                'equity': float(self.equity)
            }
            
            self.trades.append(trade_record)
            
            return True
            
        except Exception as e:
            self.logger.error(f"执行交易失败: {e}")
            return False
    
    def run_strategy(self, progress_callback=None) -> Dict:
        """运行做市策略"""
        try:
            if self.kline_data is None:
                raise ValueError("数据未加载")
            
            total_rows = len(self.kline_data)
            
            for i, row in self.kline_data.iterrows():
                timestamp = int(row['timestamp'])
                current_price = Decimal(str(row['close']))
                
                # 更新进度
                if progress_callback:
                    progress = (i + 1) / total_rows * 100
                    progress_callback(progress)
                
                # 检查爆仓
                if self.check_liquidation(current_price):
                    self.logger.warning(f"爆仓检测到，停止回测")
                    break
                
                # 计算下单量
                order_size = self.calculate_order_size(current_price)
                
                # 计算买卖价格
                bid_price = current_price * (Decimal('1') - self.bid_spread)
                ask_price = current_price * (Decimal('1') + self.ask_spread)
                
                # 做市策略逻辑：同时下买单和卖单
                net_position = self.long_position - self.short_position
                
                # 如果净仓位不大，可以继续开仓
                if abs(net_position * current_price) < self.equity * self.max_position_value_ratio:
                    # 开多单
                    if self.execute_trade(timestamp, '开多', 'buy', order_size, bid_price):
                        pass
                    
                    # 开空单
                    if self.execute_trade(timestamp, '开空', 'sell', order_size, ask_price):
                        pass
                
                # 平仓逻辑（简化）
                if abs(net_position) > order_size * 2:  # 如果净仓位过大，进行平仓
                    if net_position > 0:  # 净多头，平多
                        close_amount = min(order_size, self.long_position)
                        if close_amount > 0:
                            self.execute_trade(timestamp, '平多', 'sell', close_amount, current_price)
                    else:  # 净空头，平空
                        close_amount = min(order_size, self.short_position)
                        if close_amount > 0:
                            self.execute_trade(timestamp, '平空', 'buy', close_amount, current_price)
                
                # 记录权益曲线
                if i % 60 == 0:  # 每小时记录一次
                    self.equity_curve.append({
                        'timestamp': timestamp,
                        'equity': float(self.equity),
                        'long_position': float(self.long_position),
                        'short_position': float(self.short_position),
                        'net_position': float(self.long_position - self.short_position)
                    })
            
            # 计算最终结果
            return self.calculate_results()
            
        except Exception as e:
            self.logger.error(f"策略运行失败: {e}")
            raise
    
    def calculate_results(self) -> Dict:
        """计算回测结果"""
        try:
            # 基础指标
            total_return = (self.equity - self.initial_balance) / self.initial_balance
            total_trades = len(self.trades)
            
            # 计算胜率（简化）
            profitable_trades = 0
            for i in range(1, len(self.trades)):
                if self.trades[i]['equity'] > self.trades[i-1]['equity']:
                    profitable_trades += 1
            
            win_rate = profitable_trades / max(total_trades - 1, 1) if total_trades > 1 else 0
            
            # 计算最大回撤
            max_equity = self.initial_balance
            max_drawdown = 0
            
            for point in self.equity_curve:
                equity = point['equity']
                if equity > max_equity:
                    max_equity = equity
                else:
                    drawdown = (max_equity - equity) / max_equity
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
            
            # 计算夏普比率（简化）
            if len(self.equity_curve) > 1:
                returns = []
                for i in range(1, len(self.equity_curve)):
                    ret = (self.equity_curve[i]['equity'] - self.equity_curve[i-1]['equity']) / self.equity_curve[i-1]['equity']
                    returns.append(ret)
                
                if returns:
                    avg_return = np.mean(returns)
                    std_return = np.std(returns)
                    sharpe_ratio = avg_return / std_return if std_return > 0 else 0
                else:
                    sharpe_ratio = 0
            else:
                sharpe_ratio = 0
            
            results = {
                'total_return': float(total_return),
                'final_equity': float(self.equity),
                'total_trades': total_trades,
                'win_rate': float(win_rate),
                'max_drawdown': float(max_drawdown),
                'sharpe_ratio': float(sharpe_ratio),
                'start_date': self.start_date,
                'end_date': self.end_date,
                'initial_balance': float(self.initial_balance),
                'final_long_position': float(self.long_position),
                'final_short_position': float(self.short_position),
                'final_net_position': float(self.long_position - self.short_position),
                'trades': self.trades,
                'equity_curve': self.equity_curve
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"计算结果失败: {e}")
            raise


async def run_backtest_async(config: Dict, progress_callback=None) -> Dict:
    """异步运行回测"""
    engine = BacktestEngine(config)

    # 加载数据
    if not engine.load_data():
        raise ValueError("数据加载失败")

    # 运行策略
    results = engine.run_strategy(progress_callback)

    return results


def run_backtest_sync(config: Dict, progress_callback=None) -> Dict:
    """同步运行回测"""
    return asyncio.run(run_backtest_async(config, progress_callback))

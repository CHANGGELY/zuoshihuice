"""
市场数据服务
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.conf import settings
from typing import List, Dict, Any, Optional
import os


class MarketDataService:
    """市场数据服务类"""
    
    def __init__(self):
        self.data_root = settings.DATA_ROOT
        
    def load_kline_data(self, symbol: str = 'ETHUSDT', timeframe: str = '1m') -> Optional[pd.DataFrame]:
        """加载K线数据"""
        try:
            # 构建文件路径
            filename = f"{symbol}_{timeframe}_2019-11-01_to_2025-06-15.h5"
            file_path = self.data_root / filename
            
            if not file_path.exists():
                return None
                
            # 加载数据
            df = pd.read_hdf(file_path, key='klines')
            
            # 转换时间
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            
            # 计算额外指标
            df['quote_volume'] = df['volume'] * df['close']  # 成交额
            df['vwap'] = df['quote_volume'] / df['volume']  # 加权平均价
            
            return df
            
        except Exception as e:
            print(f"加载K线数据失败: {e}")
            return None
    
    def get_kline_data(self, symbol: str, timeframe: str, start_date: str, end_date: str, limit: int = 1000) -> List[Dict]:
        """获取指定时间范围的K线数据"""
        try:
            df = self.load_kline_data(symbol, '1m')  # 总是从1分钟数据开始
            if df is None:
                return []
            
            # 过滤时间范围
            df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)].copy()
            
            if timeframe != '1m':
                # 转换时间周期
                df = self.resample_kline_data(df, timeframe)
            
            # 限制数据量
            if len(df) > limit:
                df = df.tail(limit)
            
            # 转换为图表格式
            chart_data = []
            for _, row in df.iterrows():
                chart_data.append({
                    'time': row['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume']),
                    'quote_volume': float(row.get('quote_volume', 0)),
                    'vwap': float(row.get('vwap', row['close']))
                })
            
            return chart_data
            
        except Exception as e:
            print(f"获取K线数据失败: {e}")
            return []
    
    def resample_kline_data(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """重采样K线数据到指定时间周期"""
        try:
            # 时间周期映射
            timeframe_map = {
                '5m': '5T',
                '15m': '15T',
                '1h': '1H',
                '4h': '4H',
                '1d': '1D'
            }
            
            if timeframe not in timeframe_map:
                return df
            
            freq = timeframe_map[timeframe]
            
            # 设置时间索引
            df.set_index('datetime', inplace=True)
            
            # 重采样
            resampled = df.resample(freq).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'quote_volume': 'sum'
            }).dropna()
            
            # 重新计算加权平均价
            resampled['vwap'] = resampled['quote_volume'] / resampled['volume']
            
            # 重置索引
            resampled.reset_index(inplace=True)
            
            return resampled
            
        except Exception as e:
            print(f"重采样数据失败: {e}")
            return df
    
    def get_market_stats(self, symbol: str) -> Dict[str, Any]:
        """获取市场统计数据"""
        try:
            df = self.load_kline_data(symbol, '1m')
            if df is None:
                return {}
            
            # 获取最近24小时数据
            now = datetime.now()
            yesterday = now - timedelta(days=1)
            
            recent_data = df[df['datetime'] >= yesterday].copy()
            if len(recent_data) == 0:
                recent_data = df.tail(1440)  # 最近1440分钟（24小时）
            
            if len(recent_data) == 0:
                return {}
            
            # 计算统计指标
            latest_price = float(recent_data['close'].iloc[-1])
            first_price = float(recent_data['open'].iloc[0])
            price_change = ((latest_price - first_price) / first_price) * 100
            
            stats = {
                'symbol': symbol,
                'last_price': latest_price,
                'price_24h_change': round(price_change, 2),
                'volume_24h': float(recent_data['volume'].sum()),
                'quote_volume_24h': float(recent_data['quote_volume'].sum()),
                'high_24h': float(recent_data['high'].max()),
                'low_24h': float(recent_data['low'].min()),
                'vwap_24h': float(recent_data['vwap'].mean()),
                'updated_at': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            print(f"获取市场统计失败: {e}")
            return {}
    
    def get_supported_timeframes(self) -> List[Dict[str, str]]:
        """获取支持的时间周期"""
        return [
            {'value': '1m', 'label': '1分钟', 'description': '1分钟K线'},
            {'value': '5m', 'label': '5分钟', 'description': '5分钟K线'},
            {'value': '15m', 'label': '15分钟', 'description': '15分钟K线'},
            {'value': '1h', 'label': '1小时', 'description': '1小时K线'},
            {'value': '4h', 'label': '4小时', 'description': '4小时K线'},
            {'value': '1d', 'label': '1天', 'description': '日K线'},
        ]
    
    def get_supported_symbols(self) -> List[Dict[str, str]]:
        """获取支持的交易对"""
        return [
            {
                'symbol': 'ETHUSDT',
                'base_asset': 'ETH',
                'quote_asset': 'USDT',
                'name': 'ETH/USDT',
                'description': '以太坊对泰达币'
            },
            # 可以添加更多交易对
        ]

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        try:
            # 计算移动平均线
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma10'] = df['close'].rolling(window=10).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()

            # 计算涨跌幅和振幅
            df['price_change'] = ((df['close'] - df['open']) / df['open'] * 100).round(2)
            df['amplitude'] = ((df['high'] - df['low']) / df['open'] * 100).round(2)

            return df

        except Exception as e:
            print(f"计算技术指标失败: {e}")
            return df

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K线数据服务
提供K线数据读取、处理和VWAP计算功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os

class KlineService:
    """K线数据服务类"""
    
    def __init__(self):
        # K线数据文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
        self.data_file_path = os.path.join(
            project_root,
            'K线data',
            'ETHUSDT_1m_2019-11-01_to_2025-06-15.h5'
        )
        self._data_cache = None
        self._last_load_time = None
        
    def _load_data(self) -> pd.DataFrame:
        """加载K线数据"""
        try:
            # 检查缓存是否有效（1小时内）
            if (self._data_cache is not None and 
                self._last_load_time is not None and 
                datetime.now() - self._last_load_time < timedelta(hours=1)):
                return self._data_cache
                
            # 读取数据
            df = pd.read_hdf(self.data_file_path)
            
            # 数据预处理
            df = df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # 计算VWAP (成交额/成交量)
            # 注意：这里假设成交额 = 收盘价 * 成交量，实际应用中可能需要调整
            df['turnover'] = df['close'] * df['volume']  # 成交额
            df['vwap'] = np.where(df['volume'] > 0, df['turnover'] / df['volume'], df['close'])
            
            # 计算涨跌幅和振幅
            df['price_change'] = df['close'] - df['open']
            df['price_change_pct'] = np.where(df['open'] > 0, (df['close'] - df['open']) / df['open'] * 100, 0)
            df['amplitude'] = np.where(df['low'] > 0, (df['high'] - df['low']) / df['low'] * 100, 0)
            
            # 缓存数据
            self._data_cache = df
            self._last_load_time = datetime.now()
            
            return df
            
        except Exception as e:
            print(f"加载K线数据失败: {e}")
            return pd.DataFrame()
    
    def get_kline_data(self, 
                      start_time: Optional[str] = None, 
                      end_time: Optional[str] = None,
                      timeframe: str = '1m',
                      limit: int = 1000) -> List[Dict]:
        """
        获取K线数据
        
        Args:
            start_time: 开始时间 (YYYY-MM-DD HH:MM:SS)
            end_time: 结束时间 (YYYY-MM-DD HH:MM:SS)
            timeframe: 时间周期 (1m, 5m, 15m, 1h, 4h, 1d)
            limit: 最大返回条数
            
        Returns:
            K线数据列表
        """
        df = self._load_data()
        if df.empty:
            return []
        
        # 时间过滤
        if start_time:
            df = df[df.index >= pd.to_datetime(start_time)]
        if end_time:
            df = df[df.index <= pd.to_datetime(end_time)]
        
        # 时间周期重采样
        if timeframe != '1m':
            df = self._resample_data(df, timeframe)
        
        # 限制返回条数
        if len(df) > limit:
            df = df.tail(limit)
        
        # 转换为前端需要的格式
        result = []
        for timestamp, row in df.iterrows():
            result.append({
                'time': int(timestamp.timestamp()),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume']),
                'turnover': float(row['turnover']),
                'vwap': float(row['vwap']),
                'price_change': float(row['price_change']),
                'price_change_pct': float(row['price_change_pct']),
                'amplitude': float(row['amplitude'])
            })
        
        return result
    
    def _resample_data(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """重采样数据到指定时间周期"""
        # 时间周期映射
        freq_map = {
            '1m': '1min',
            '5m': '5min',
            '15m': '15min',
            '1h': '1H',
            '4h': '4H',
            '1d': '1D'
        }
        
        freq = freq_map.get(timeframe, '1min')
        
        # 重采样规则
        agg_rules = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'turnover': 'sum'
        }
        
        resampled = df.resample(freq).agg(agg_rules)
        
        # 重新计算VWAP等指标
        resampled['vwap'] = np.where(
            resampled['volume'] > 0, 
            resampled['turnover'] / resampled['volume'], 
            resampled['close']
        )
        resampled['price_change'] = resampled['close'] - resampled['open']
        resampled['price_change_pct'] = np.where(
            resampled['open'] > 0, 
            (resampled['close'] - resampled['open']) / resampled['open'] * 100, 
            0
        )
        resampled['amplitude'] = np.where(
            resampled['low'] > 0, 
            (resampled['high'] - resampled['low']) / resampled['low'] * 100, 
            0
        )
        
        # 删除空数据
        resampled = resampled.dropna()
        
        return resampled
    
    def get_data_range(self) -> Dict:
        """获取数据时间范围"""
        df = self._load_data()
        if df.empty:
            return {}
        
        return {
            'start_time': df.index.min().strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': df.index.max().strftime('%Y-%m-%d %H:%M:%S'),
            'total_records': len(df)
        }
    
    def get_latest_price(self) -> Dict:
        """获取最新价格信息"""
        df = self._load_data()
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        return {
            'symbol': 'ETH/USDC',
            'price': float(latest['close']),
            'change': float(latest['close'] - prev['close']),
            'change_pct': float((latest['close'] - prev['close']) / prev['close'] * 100) if prev['close'] > 0 else 0,
            'volume_24h': float(df.tail(1440)['volume'].sum()),  # 24小时成交量
            'turnover_24h': float(df.tail(1440)['turnover'].sum()),  # 24小时成交额
            'high_24h': float(df.tail(1440)['high'].max()),
            'low_24h': float(df.tail(1440)['low'].min()),
            'timestamp': int(latest.name.timestamp())
        }

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场数据API路由
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

try:
    from core.config import settings
except ImportError:
    from fastapi_backend.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class KlineData(BaseModel):
    """K线数据模型"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: float
    vwap: float
    price_change: float
    price_change_pct: float
    amplitude: float

class MarketDataService:
    """市场数据服务"""
    
    def __init__(self):
        self.data_file = settings.data_file
        self._cache = None
        self._cache_time = None
        self._cache_ttl = 3600  # 1小时缓存
    
    def _load_data(self) -> pd.DataFrame:
        """加载K线数据"""
        try:
            # 检查缓存
            if (self._cache is not None and 
                self._cache_time is not None and 
                (datetime.now() - self._cache_time).seconds < self._cache_ttl):
                return self._cache
            
            if not self.data_file.exists():
                raise FileNotFoundError(f"数据文件不存在: {self.data_file}")
            
            logger.info("📊 加载K线数据...")
            df = pd.read_hdf(self.data_file)
            
            # 数据预处理
            df = df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # 计算额外指标
            df['turnover'] = df['close'] * df['volume']  # 成交额
            df['vwap'] = np.where(df['volume'] > 0, df['turnover'] / df['volume'], df['close'])
            df['price_change'] = df['close'] - df['open']
            df['price_change_pct'] = np.where(df['open'] > 0, (df['close'] - df['open']) / df['open'] * 100, 0)
            df['amplitude'] = np.where(df['low'] > 0, (df['high'] - df['low']) / df['low'] * 100, 0)
            
            # 缓存数据
            self._cache = df
            self._cache_time = datetime.now()
            
            logger.info(f"✅ K线数据加载成功，共 {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"❌ 加载K线数据失败: {e}")
            raise
    
    def get_klines(self, 
                   symbol: str = "ETHUSDT",
                   timeframe: str = "1m", 
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   limit: int = 1000) -> List[Dict[str, Any]]:
        """获取K线数据"""
        try:
            df = self._load_data()
            
            # 时间范围过滤
            if start_date:
                start_dt = pd.to_datetime(start_date)
                df = df[df.index >= start_dt]
            
            if end_date:
                end_dt = pd.to_datetime(end_date)
                df = df[df.index <= end_dt]
            
            # 限制数量
            if len(df) > limit:
                df = df.tail(limit)
            
            # 时间周期转换
            if timeframe != "1m":
                df = self._resample_timeframe(df, timeframe)
            
            # 转换为列表
            result = []
            for timestamp, row in df.iterrows():
                result.append({
                    "timestamp": int(timestamp.timestamp()),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": float(row['volume']),
                    "turnover": float(row['turnover']),
                    "vwap": float(row['vwap']),
                    "price_change": float(row['price_change']),
                    "price_change_pct": float(row['price_change_pct']),
                    "amplitude": float(row['amplitude'])
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 获取K线数据失败: {e}")
            raise
    
    def _resample_timeframe(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """重采样时间周期"""
        timeframe_map = {
            "1m": "1T",
            "5m": "5T", 
            "15m": "15T",
            "1h": "1H",
            "4h": "4H",
            "1d": "1D"
        }
        
        if timeframe not in timeframe_map:
            raise ValueError(f"不支持的时间周期: {timeframe}")
        
        freq = timeframe_map[timeframe]
        
        # 重采样
        resampled = df.resample(freq).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'turnover': 'sum'
        }).dropna()
        
        # 重新计算指标
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
        
        return resampled
    
    def get_market_stats(self) -> Dict[str, Any]:
        """获取市场统计信息"""
        try:
            df = self._load_data()
            
            # 最新数据
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # 24小时统计
            day_ago = df.index[-1] - timedelta(days=1)
            day_data = df[df.index >= day_ago]
            
            return {
                "symbol": "ETHUSDT",
                "latest_price": float(latest['close']),
                "price_change_24h": float(latest['close'] - day_data.iloc[0]['close']),
                "price_change_pct_24h": float((latest['close'] - day_data.iloc[0]['close']) / day_data.iloc[0]['close'] * 100),
                "high_24h": float(day_data['high'].max()),
                "low_24h": float(day_data['low'].min()),
                "volume_24h": float(day_data['volume'].sum()),
                "turnover_24h": float(day_data['turnover'].sum()),
                "vwap_24h": float(day_data['turnover'].sum() / day_data['volume'].sum()),
                "data_range": {
                    "start": df.index[0].isoformat(),
                    "end": df.index[-1].isoformat(),
                    "total_records": len(df)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 获取市场统计失败: {e}")
            raise

# 全局市场数据服务
market_service = MarketDataService()

@router.get("/klines", summary="获取K线数据")
async def get_klines(
    symbol: str = Query(default="ETHUSDT", description="交易对"),
    timeframe: str = Query(default="1m", description="时间周期"),
    start_date: Optional[str] = Query(default=None, description="开始日期"),
    end_date: Optional[str] = Query(default=None, description="结束日期"),
    limit: int = Query(default=1000, ge=1, le=10000, description="数量限制")
):
    """
    获取K线数据
    
    - **symbol**: 交易对 (目前只支持ETHUSDT)
    - **timeframe**: 时间周期 (1m, 5m, 15m, 1h, 4h, 1d)
    - **start_date**: 开始日期 (YYYY-MM-DD)
    - **end_date**: 结束日期 (YYYY-MM-DD)
    - **limit**: 数量限制 (1-10000)
    """
    try:
        klines = market_service.get_klines(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "count": len(klines),
            "data": klines
        }
        
    except Exception as e:
        logger.error(f"❌ K线数据API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", summary="获取市场统计")
async def get_market_stats():
    """获取市场统计信息"""
    try:
        stats = market_service.get_market_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ 市场统计API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols", summary="获取交易对列表")
async def get_symbols():
    """获取支持的交易对列表"""
    return {
        "success": True,
        "symbols": ["ETHUSDT"],
        "default": "ETHUSDT"
    }

@router.get("/timeframes", summary="获取时间周期列表")
async def get_timeframes():
    """获取支持的时间周期列表"""
    return {
        "success": True,
        "timeframes": [
            {"value": "1m", "label": "1分钟"},
            {"value": "5m", "label": "5分钟"},
            {"value": "15m", "label": "15分钟"},
            {"value": "1h", "label": "1小时"},
            {"value": "4h", "label": "4小时"},
            {"value": "1d", "label": "1天"}
        ],
        "default": "1m"
    }

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安永续合约历史K线数据采集脚本
获取 ETHUSDT 永续合约 1分钟周期全量历史数据，包含真实成交额

数据字段说明:
1. open_time: 开盘时间 (毫秒时间戳)
2. open: 开盘价
3. high: 最高价  
4. low: 最低价
5. close: 收盘价
6. volume: 基础资产成交量 (ETH)
7. close_time: 收盘时间 (毫秒时间戳)
8. quote_asset_volume: 计价资产成交额 (USDT)
9. count: 交易笔数
10. taker_buy_base_asset_volume: 主动买方基础成交量
11. taker_buy_quote_asset_volume: 主动买方计价成交额
12. ignore: 忽略字段
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import time
import h5py
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from decimal import Decimal
import argparse
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fetch_binance_klines.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BinanceKlinesFetcher:
    """币安永续合约K线数据采集器"""
    
    def __init__(self):
        self.base_url = os.getenv('BINANCE_FAPI_BASE_URL', 'https://fapi.binance.com')
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = float(os.getenv('BINANCE_FAPI_RATE_DELAY_SEC', '0.1'))  # 速率延迟，默认100ms
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'python-binance-klines-fetcher/1.0'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    async def get_server_time(self) -> int:
        """获取币安服务器时间"""
        url = f"{self.base_url}/fapi/v1/time"
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data['serverTime']
            else:
                raise Exception(f"获取服务器时间失败: {response.status}")
    
    async def get_earliest_valid_timestamp(self, symbol: str) -> int:
        """获取交易对的最早有效时间戳"""
        url = f"{self.base_url}/fapi/v1/klines"
        params = {
            'symbol': symbol,
            'interval': '1m',
            'limit': 1
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data:
                    return data[0][0]  # 返回第一根K线的开盘时间
            raise Exception(f"获取最早时间戳失败: {response.status}")
    
    async def fetch_klines_batch(
        self, 
        symbol: str, 
        start_time: int, 
        end_time: int,
        interval: str = '1m',
        limit: int = 1500
    ) -> List[List]:
        """
        获取单批次K线数据
        
        Args:
            symbol: 交易对符号
            start_time: 开始时间戳(毫秒)
            end_time: 结束时间戳(毫秒)
            interval: K线间隔
            limit: 每次请求的最大数量
        """
        url = f"{self.base_url}/fapi/v1/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time,
            'limit': limit
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"获取到 {len(data)} 条数据，时间范围: {start_time} - {end_time}")
                    return data
                elif response.status == 429:
                    # 触发限流，等待更长时间
                    logger.warning("触发API限流，等待10秒后重试")
                    await asyncio.sleep(10)
                    return await self.fetch_klines_batch(symbol, start_time, end_time, interval, limit)
                else:
                    logger.error(f"API请求失败: {response.status}, {await response.text()}")
                    return []
        except Exception as e:
            logger.error(f"请求异常: {e}")
            return []
        finally:
            # 速率限制
            await asyncio.sleep(self.rate_limit_delay)
    
    async def fetch_all_klines(
        self, 
        symbol: str, 
        start_date: str = None,
        end_date: str = None,
        interval: str = '1m',
        checkpoint_mode: bool = True,
        segment_days: int = 30
    ) -> pd.DataFrame:
        """
        获取全量历史K线数据，支持断点续传和分段处理
        
        Args:
            symbol: 交易对符号 (如 'ETHUSDT')
            start_date: 开始日期 (格式: 'YYYY-MM-DD')，None表示从最早开始
            end_date: 结束日期 (格式: 'YYYY-MM-DD')，None表示到当前时间
            interval: K线间隔
            checkpoint_mode: 是否启用断点续传
            segment_days: 分段天数，避免内存占用过大
        """
        logger.info(f"开始获取 {symbol} {interval} 历史数据 (断点续传: {checkpoint_mode})")
        
        # 检查断点续传
        checkpoint_start = None
        if checkpoint_mode:
            checkpoint_start = load_checkpoint(symbol, interval)
        
        # 确定时间范围
        if start_date and not checkpoint_start:
            start_time = int(datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc).timestamp() * 1000)
        elif checkpoint_start:
            start_time = checkpoint_start
            logger.info(f"从断点继续: {start_time} ({datetime.fromtimestamp(start_time/1000, tz=timezone.utc)})")
        else:
            start_time = await self.get_earliest_valid_timestamp(symbol)
            logger.info(f"使用最早有效时间戳: {start_time} ({datetime.fromtimestamp(start_time/1000, tz=timezone.utc)})")
        
        if end_date:
            end_time = int(datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc).timestamp() * 1000)
        else:
            end_time = await self.get_server_time()
            logger.info(f"使用当前服务器时间: {end_time} ({datetime.fromtimestamp(end_time/1000, tz=timezone.utc)})")
        
        # 分段处理
        segment_ms = segment_days * 24 * 60 * 60 * 1000
        all_segments = []
        current_start = start_time
        
        while current_start < end_time:
            current_end = min(current_start + segment_ms - 1, end_time)
            
            logger.info(f"处理分段: {datetime.fromtimestamp(current_start/1000, tz=timezone.utc)} 到 {datetime.fromtimestamp(current_end/1000, tz=timezone.utc)}")
            
            segment_df = await self._fetch_segment(symbol, current_start, current_end, interval)
            
            if not segment_df.empty:
                all_segments.append(segment_df)
                
                # 保存断点
                if checkpoint_mode:
                    save_checkpoint(symbol, interval, int(segment_df['open_time'].max().timestamp() * 1000))
            
            current_start = current_end + 1
        
        # 合并所有分段
        if all_segments:
            df = pd.concat(all_segments, ignore_index=True)
            df = df.drop_duplicates('open_time').sort_values('open_time').reset_index(drop=True)
            logger.info(f"合并完成，总计 {len(df)} 条K线数据")
        else:
            df = pd.DataFrame()
        
        # 数据验证
        if not df.empty:
            self._validate_klines_data(df, symbol, interval)
        
        return df
    
    async def _fetch_segment(self, symbol: str, start_time: int, end_time: int, interval: str) -> pd.DataFrame:
        """获取单个时间段的K线数据"""
        interval_ms = self._interval_to_milliseconds(interval)
        batch_size = 1500
        batch_duration = interval_ms * batch_size
        
        all_klines = []
        current_start = start_time
        
        while current_start < end_time:
            current_end = min(current_start + batch_duration - 1, end_time)
            
            batch_data = await self.fetch_klines_batch(
                symbol, current_start, current_end, interval, batch_size
            )
            
            if batch_data:
                all_klines.extend(batch_data)
                last_kline_time = batch_data[-1][0]
                current_start = last_kline_time + interval_ms
            else:
                current_start = current_end + 1
        
        if all_klines:
            return self._klines_to_dataframe(all_klines)
        else:
            return pd.DataFrame()
    
    async def fetch_incremental_update(self, symbol: str, interval: str = '1m', days_back: int = 2) -> pd.DataFrame:
        """
        增量更新：获取最近几天的数据
        
        Args:
            symbol: 交易对符号
            interval: K线间隔  
            days_back: 回溯天数，默认2天确保覆盖昨天和今天
        """
        logger.info(f"开始增量更新 {symbol} {interval}，回溯 {days_back} 天")
        
        # 计算时间范围
        now = datetime.now(timezone.utc)
        start_time = int((now - pd.Timedelta(days=days_back)).timestamp() * 1000)
        end_time = int(now.timestamp() * 1000)
        
        logger.info(f"增量更新范围: {datetime.fromtimestamp(start_time/1000, tz=timezone.utc)} 到 {datetime.fromtimestamp(end_time/1000, tz=timezone.utc)}")
        
        return await self._fetch_segment(symbol, start_time, end_time, interval)
    
    def _interval_to_milliseconds(self, interval: str) -> int:
        """将间隔字符串转换为毫秒数"""
        interval_map = {
            '1m': 60 * 1000,
            '3m': 3 * 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '30m': 30 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '2h': 2 * 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '6h': 6 * 60 * 60 * 1000,
            '8h': 8 * 60 * 60 * 1000,
            '12h': 12 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000,
        }
        return interval_map.get(interval, 60 * 1000)
    
    def _klines_to_dataframe(self, klines: List[List]) -> pd.DataFrame:
        """将K线数据转换为DataFrame"""
        columns = [
            'open_time',           # 开盘时间
            'open',                # 开盘价
            'high',                # 最高价
            'low',                 # 最低价
            'close',               # 收盘价
            'volume',              # 基础资产成交量
            'close_time',          # 收盘时间
            'quote_asset_volume',  # 计价资产成交额
            'count',               # 交易笔数
            'taker_buy_base_asset_volume',   # 主动买方基础成交量
            'taker_buy_quote_asset_volume',  # 主动买方计价成交额
            'ignore'               # 忽略字段
        ]
        
        df = pd.DataFrame(klines, columns=columns)
        
        # 数据类型转换
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms', utc=True)
        
        # 价格和成交量字段转换为浮点数
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume', 
                          'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 整数字段 -> 使用Int64方便包含NA；保存到HDF5时再统一转float64
        df['count'] = pd.to_numeric(df['count'], errors='coerce').astype('Int64')
        
        # 删除忽略字段
        df = df.drop('ignore', axis=1)
        
        # 按时间排序并去重
        df = df.sort_values('open_time').drop_duplicates('open_time').reset_index(drop=True)
        
        return df
    
    def _validate_klines_data(self, df: pd.DataFrame, symbol: str, interval: str):
        """验证K线数据的完整性和正确性"""
        logger.info(f"开始验证 {symbol} {interval} 数据...")
        
        if df.empty:
            logger.error("数据为空！")
            return
        
        # 基本统计
        logger.info(f"数据行数: {len(df)}")
        logger.info(f"时间范围: {df['open_time'].min()} 到 {df['open_time'].max()}")
        logger.info(f"价格范围: {df['low'].min():.4f} - {df['high'].max():.4f}")
        
        # 检查缺失值
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            logger.warning(f"发现缺失值:\n{missing_data[missing_data > 0]}")
        
        # 检查价格异常
        price_issues = 0
        invalid_ohlc = df[(df['open'] <= 0) | (df['high'] <= 0) | (df['low'] <= 0) | (df['close'] <= 0)]
        if not invalid_ohlc.empty:
            price_issues += len(invalid_ohlc)
            logger.warning(f"发现 {len(invalid_ohlc)} 条价格异常数据（<=0）")
        
        invalid_hl = df[df['high'] < df['low']]
        if not invalid_hl.empty:
            price_issues += len(invalid_hl)
            logger.warning(f"发现 {len(invalid_hl)} 条高低价异常数据（high < low）")
        
        # 检查成交量异常
        invalid_volume = df[(df['volume'] < 0) | (df['quote_asset_volume'] < 0)]
        if not invalid_volume.empty:
            logger.warning(f"发现 {len(invalid_volume)} 条成交量异常数据（<0）")
        
        # 检查时间连续性（针对1分钟数据）
        if interval == '1m':
            df_sorted = df.sort_values('open_time')
            time_diff = df_sorted['open_time'].diff().dt.total_seconds()
            expected_diff = 60  # 1分钟 = 60秒
            
            # 允许5秒的误差
            irregular_intervals = time_diff[(time_diff < expected_diff - 5) | (time_diff > expected_diff + 5)]
            if not irregular_intervals.empty:
                logger.warning(f"发现 {len(irregular_intervals)} 个不规则时间间隔")
        
        # 计算VWAP验证
        df['vwap'] = df['quote_asset_volume'] / df['volume']
        vwap_issues = df[(df['vwap'] < df['low']) | (df['vwap'] > df['high'])]
        if not vwap_issues.empty:
            logger.warning(f"发现 {len(vwap_issues)} 条VWAP异常数据（超出高低价范围）")
        
        logger.info(f"数据验证完成，发现 {price_issues} 个价格问题")

def save_to_h5(df: pd.DataFrame, filename: str, symbol: str = 'ETHUSDT', interval: str = '1m'):
    """保存数据到HDF5格式（精简为8个核心字段）"""
    logger.info(f"保存数据到 {filename}")
    
    # 转换时间戳为毫秒Unix时间戳
    df_save = df.copy()
    df_save['open_time_ms'] = df_save['open_time'].astype('int64') // 10**6
    df_save['close_time_ms'] = df_save['close_time'].astype('int64') // 10**6
    
    # 精简为用户指定的8个核心字段
    columns_ordered = [
        'open_time_ms',        # 1. open time (毫秒时间戳)
        'open',                # 2. open
        'high',                # 3. high
        'low',                 # 4. low
        'close',               # 5. close
        'volume',              # 6. volume (基准货币成交量)
        'close_time_ms',       # 7. close time (毫秒时间戳)
        'quote_asset_volume'   # 8. quote asset volume (计价货币成交额)
    ]
    
    df_save = df_save[columns_ordered]
    
    # 将所有列统一为float64
    for col in df_save.columns:
        df_save[col] = pd.to_numeric(df_save[col], errors='coerce').astype('float64')
    
    data_array = df_save.to_numpy(dtype=np.float64)
    
    # 保存为HDF5（开启压缩和分块）
    with h5py.File(filename, 'w') as f:
        dataset = f.create_dataset(
            'kline_data', 
            data=data_array, 
            dtype='float64', 
            compression='gzip', 
            compression_opts=4, 
            shuffle=True,
            chunks=True
        )
        
        # 添加属性信息
        dataset.attrs['columns'] = [col.encode('utf-8') for col in columns_ordered]
        dataset.attrs['symbol'] = symbol.encode('utf-8')
        dataset.attrs['interval'] = interval.encode('utf-8')
        dataset.attrs['source'] = 'binance_futures'
        dataset.attrs['created_at'] = datetime.now(timezone.utc).isoformat()
        dataset.attrs['total_records'] = len(df_save)
        dataset.attrs['start_time'] = df['open_time'].min().isoformat()
        dataset.attrs['end_time'] = df['open_time'].max().isoformat()
    
    logger.info(f"已保存 {len(df_save)} 条记录到 {filename}")

def append_to_h5(df: pd.DataFrame, filename: str):
    """追加数据到现有HDF5文件"""
    if not Path(filename).exists():
        logger.warning(f"文件 {filename} 不存在，将创建新文件")
        return save_to_h5(df, filename)
    
    logger.info(f"追加 {len(df)} 条记录到 {filename}")
    
    # 读取现有数据与属性
    with h5py.File(filename, 'r') as f:
        existing_data = f['kline_data'][:]
        columns = [col.decode('utf-8') for col in f['kline_data'].attrs['columns']]
        old_attrs = {k: v for k, v in f['kline_data'].attrs.items()}
    existing_df = pd.DataFrame(existing_data, columns=columns)
    
    # 转换新数据
    df_new = df.copy()
    df_new['open_time_ms'] = df_new['open_time'].astype('int64') // 10**6
    df_new['close_time_ms'] = df_new['close_time'].astype('int64') // 10**6
    
    columns_ordered = [
        'open_time_ms', 'open', 'high', 'low', 'close', 'volume', 
        'close_time_ms', 'quote_asset_volume'
    ]
    df_new = df_new[columns_ordered]
    
    for col in df_new.columns:
        df_new[col] = pd.to_numeric(df_new[col], errors='coerce').astype('float64')
    
    # 合并数据并去重
    combined_df = pd.concat([existing_df, df_new], ignore_index=True)
    combined_df = combined_df.drop_duplicates('open_time_ms').sort_values('open_time_ms').reset_index(drop=True)
    
    # 重写文件
    data_array = combined_df.to_numpy(dtype=np.float64)
    with h5py.File(filename, 'w') as f:
        dataset = f.create_dataset(
            'kline_data', 
            data=data_array, 
            dtype='float64', 
            compression='gzip', 
            compression_opts=4, 
            shuffle=True,
            chunks=True
        )
        
        # 恢复/更新属性
        dataset.attrs['columns'] = [col.encode('utf-8') for col in columns_ordered]
        # 恢复旧属性（若存在）
        for k, v in old_attrs.items():
            if k in ['columns', 'total_records', 'start_time', 'end_time']:
                continue
            dataset.attrs[k] = v
        # 更新计数与时间范围
        dataset.attrs['total_records'] = len(combined_df)
        start_ts_ms = int(combined_df['open_time_ms'].min())
        end_ts_ms = int(combined_df['open_time_ms'].max())
        dataset.attrs['start_time'] = pd.to_datetime(start_ts_ms, unit='ms', utc=True).isoformat()
        dataset.attrs['end_time'] = pd.to_datetime(end_ts_ms, unit='ms', utc=True).isoformat()
    
    logger.info(f"追加完成，总计 {len(combined_df)} 条记录")

def save_checkpoint(symbol: str, interval: str, last_timestamp: int):
    """保存断点续传信息"""
    checkpoint_file = f".checkpoint_{symbol}_{interval}.json"
    checkpoint_data = {
        'symbol': symbol,
        'interval': interval,
        'last_timestamp': last_timestamp,
        'last_update': datetime.now(timezone.utc).isoformat()
    }
    with open(checkpoint_file, 'w') as f:
        json.dump(checkpoint_data, f, indent=2)
    logger.info(f"保存断点: {last_timestamp} ({datetime.fromtimestamp(last_timestamp/1000, tz=timezone.utc)})")

def load_checkpoint(symbol: str, interval: str) -> Optional[int]:
    """加载断点续传信息"""
    checkpoint_file = f".checkpoint_{symbol}_{interval}.json"
    if Path(checkpoint_file).exists():
        try:
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
            logger.info(f"加载断点: {data['last_timestamp']} ({datetime.fromtimestamp(data['last_timestamp']/1000, tz=timezone.utc)})")
            return data['last_timestamp']
        except Exception as e:
            logger.warning(f"加载断点失败: {e}")
    return None

def save_to_csv(df: pd.DataFrame, filename: str):
    """保存数据到CSV格式"""
    logger.info(f"保存数据到 {filename}")
    df.to_csv(filename, index=False, date_format='%Y-%m-%d %H:%M:%S')
    logger.info(f"已保存 {len(df)} 条记录到 {filename}")

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Fetch Binance Futures klines and save to HDF5/CSV')
    parser.add_argument('--symbol', type=str, default='ETHUSDT', help='交易对，如 ETHUSDT')
    parser.add_argument('--interval', type=str, default='1m', help='K线周期，如 1m/5m/1h')
    parser.add_argument('--start', type=str, default=None, help='开始日期，例如 2019-11-01 (UTC)')
    parser.add_argument('--end', type=str, default=None, help='结束日期，例如 2025-06-15 (UTC)')
    parser.add_argument('--out-prefix', type=str, default=None, help='输出文件名前缀；默认基于symbol与时间范围自动生成')
    parser.add_argument('--mode', type=str, choices=['full', 'incremental', 'daemon'], default='full', help='运行模式：全量/增量/守护')
    parser.add_argument('--save-csv', action='store_true', help='是否同时保存CSV（默认不保存）')
    parser.add_argument('--days-back', type=int, default=2, help='增量更新回溯天数，默认2天覆盖昨日/今日')
    parser.add_argument('--segment-days', type=int, default=30, help='全量抓取分段天数，默认30天')
    parser.add_argument('--no-checkpoint', action='store_true', help='禁用断点续传（默认启用）')
    parser.add_argument('--update-interval-min', type=int, default=15, help='守护模式下增量更新间隔分钟，默认15分钟')
    args = parser.parse_args()

    symbol = args.symbol.upper()
    interval = args.interval
    start_date = args.start
    end_date = args.end
    checkpoint_mode = not args.no_checkpoint

    logger.info(f"开始获取币安{symbol}永续合约历史数据 interval={interval} start={start_date} end={end_date} mode={args.mode}")
    
    try:
        async with BinanceKlinesFetcher() as fetcher:
            if args.mode == 'full':
                # 获取历史数据（全量）
                df = await fetcher.fetch_all_klines(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    interval=interval,
                    checkpoint_mode=checkpoint_mode,
                    segment_days=args.segment_days
                )
                
                if df.empty:
                    logger.error("未获取到任何数据")
                    return
                
                # 生成文件名（包含实际时间范围）
                start_date_actual = df['open_time'].min().strftime('%Y-%m-%d')
                end_date_actual = df['open_time'].max().strftime('%Y-%m-%d')
                
                if args.out_prefix:
                    base_filename = f"{args.out_prefix}_{start_date_actual}_to_{end_date_actual}"
                else:
                    base_filename = f"{symbol}_{interval}_{start_date_actual}_to_{end_date_actual}_complete"
                
                h5_filename = f"{base_filename}.h5"
                
                # 仅保存H5；CSV可选
                save_to_h5(df, h5_filename, symbol=symbol, interval=interval)
                if args.save_csv:
                    csv_filename = f"{base_filename}.csv"
                    save_to_csv(df, csv_filename)
                
                # 输出汇总信息
                logger.info("=" * 60)
                logger.info("数据获取完成汇总:")
                logger.info(f"交易对: {symbol} (永续合约)")
                logger.info(f"周期: {interval}")
                logger.info(f"数据条数: {len(df):,}")
                logger.info(f"时间范围: {df['open_time'].min()} 到 {df['open_time'].max()}")
                logger.info(f"数据文件: {h5_filename}")
                logger.info(f"包含字段: {list(df.columns)}")
                logger.info("=" * 60)
            elif args.mode == 'incremental':
                # 增量更新（覆盖昨日+今日），落盘到稳定文件名
                df = await fetcher.fetch_incremental_update(symbol=symbol, interval=interval, days_back=args.days_back)
                if df.empty:
                    logger.warning("增量更新未返回数据")
                    return
                target_h5 = f"{symbol}_{interval}_complete.h5"
                append_to_h5(df, target_h5)
                logger.info("=" * 60)
                logger.info("增量更新完成汇总:")
                logger.info(f"交易对: {symbol} (永续合约)")
                logger.info(f"周期: {interval}")
                logger.info(f"数据条数(本次): {len(df):,}")
                logger.info(f"时间范围(本次): {df['open_time'].min()} 到 {df['open_time'].max()}")
                logger.info(f"数据文件: {target_h5}")
                logger.info("=" * 60)
            else:  # daemon
                # 守护模式：周期性增量更新
                target_h5 = f"{symbol}_{interval}_complete.h5"
                logger.info(f"进入守护模式：每 {args.update_interval_min} 分钟执行一次增量更新，目标文件 {target_h5}")
                while True:
                    try:
                        df = await fetcher.fetch_incremental_update(symbol=symbol, interval=interval, days_back=args.days_back)
                        if not df.empty:
                            append_to_h5(df, target_h5)
                            logger.info(f"守护模式一次更新完成，写入 {len(df)} 条 [{df['open_time'].min()} ~ {df['open_time'].max()}]")
                        else:
                            logger.info("守护模式本次无新数据")
                    except Exception as e:
                        logger.error(f"守护模式更新异常: {e}")
                    await asyncio.sleep(args.update_interval_min * 60)
    except Exception as e:
        logger.error(f"获取数据时发生错误: {e}")
        raise

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
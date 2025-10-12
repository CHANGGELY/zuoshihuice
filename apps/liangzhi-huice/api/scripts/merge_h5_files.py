#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H5文件合并脚本
将多个H5文件合并为单一完整文件
"""

import h5py
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import logging
import argparse
from pathlib import Path
from typing import List, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def read_h5_file(filepath: str) -> Tuple[pd.DataFrame, dict]:
    """读取H5文件并返回DataFrame和属性信息"""
    logger.info(f"读取文件: {filepath}")
    
    with h5py.File(filepath, 'r') as f:
        data = f['kline_data'][:]
        # 兼容 bytes 或 str 两种存储格式
        raw_cols = f['kline_data'].attrs['columns']
        columns = [c.decode('utf-8') if isinstance(c, (bytes, bytearray)) else str(c) for c in raw_cols]
        attrs = {k: v for k, v in f['kline_data'].attrs.items()}
    
    df = pd.DataFrame(data, columns=columns)
    logger.info(f"文件 {Path(filepath).name} 包含 {len(df)} 条记录")
    logger.info(f"时间范围: {pd.to_datetime(df['open_time_ms'], unit='ms', utc=True).min()} 到 {pd.to_datetime(df['open_time_ms'], unit='ms', utc=True).max()}")
    
    return df, attrs

def merge_h5_files(input_files: List[str], output_file: str, symbol: str = 'ETHUSDT', interval: str = '1m'):
    """合并多个H5文件"""
    logger.info(f"开始合并 {len(input_files)} 个H5文件")
    
    all_dataframes = []
    base_attrs = None
    
    # 读取所有输入文件
    for filepath in input_files:
        if not Path(filepath).exists():
            logger.error(f"文件不存在: {filepath}")
            continue
            
        df, attrs = read_h5_file(filepath)
        if not df.empty:
            all_dataframes.append(df)
            if base_attrs is None:
                base_attrs = attrs
    
    if not all_dataframes:
        logger.error("没有有效的输入文件")
        return
    
    # 合并所有数据
    logger.info("合并数据中...")
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # 去重并排序
    logger.info("去重和排序...")
    initial_count = len(combined_df)
    combined_df = combined_df.drop_duplicates('open_time_ms').sort_values('open_time_ms').reset_index(drop=True)
    final_count = len(combined_df)
    
    if initial_count != final_count:
        logger.info(f"去重完成，从 {initial_count} 条减少到 {final_count} 条，去除 {initial_count - final_count} 条重复")
    
    # 数据验证
    logger.info("数据验证...")
    start_time = pd.to_datetime(combined_df['open_time_ms'], unit='ms', utc=True).min()
    end_time = pd.to_datetime(combined_df['open_time_ms'], unit='ms', utc=True).max()
    
    logger.info(f"合并后数据统计:")
    logger.info(f"  总记录数: {len(combined_df):,}")
    logger.info(f"  时间范围: {start_time} 到 {end_time}")
    logger.info(f"  数据列: {list(combined_df.columns)}")
    
    # 检查数据连续性（针对1分钟数据）
    if interval == '1m':
        time_series = pd.to_datetime(combined_df['open_time_ms'], unit='ms', utc=True)
        time_diff = time_series.diff().dt.total_seconds()
        expected_diff = 60  # 1分钟
        
        irregular_count = ((time_diff < 55) | (time_diff > 65)).sum()
        if irregular_count > 0:
            logger.warning(f"发现 {irregular_count} 个不规则时间间隔（非60秒±5秒）")
    
    # 保存合并文件
    logger.info(f"保存合并结果到 {output_file}")
    data_array = combined_df.to_numpy(dtype=np.float64)
    
    with h5py.File(output_file, 'w') as f:
        dataset = f.create_dataset(
            'kline_data', 
            data=data_array, 
            dtype='float64', 
            compression='gzip', 
            compression_opts=4, 
            shuffle=True,
            chunks=True
        )
        
        # 设置属性
        dataset.attrs['columns'] = [col.encode('utf-8') for col in combined_df.columns]
        dataset.attrs['symbol'] = symbol.encode('utf-8')
        dataset.attrs['interval'] = interval.encode('utf-8')
        dataset.attrs['source'] = 'binance_futures'
        dataset.attrs['created_at'] = datetime.now(timezone.utc).isoformat()
        dataset.attrs['total_records'] = len(combined_df)
        dataset.attrs['start_time'] = start_time.isoformat()
        dataset.attrs['end_time'] = end_time.isoformat()
        dataset.attrs['merged_files'] = len(input_files)
    
    logger.info("=" * 60)
    logger.info("合并完成!")
    logger.info(f"输出文件: {output_file}")
    logger.info(f"总记录数: {len(combined_df):,}")
    logger.info(f"时间范围: {start_time} 到 {end_time}")
    logger.info(f"文件大小: {Path(output_file).stat().st_size / (1024*1024):.1f} MB")
    logger.info("=" * 60)

def main():
    parser = argparse.ArgumentParser(description='合并多个H5 K线数据文件')
    parser.add_argument('input_files', nargs='+', help='要合并的输入H5文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出文件路径')
    parser.add_argument('--symbol', default='ETHUSDT', help='交易对符号')
    parser.add_argument('--interval', default='1m', help='K线间隔')
    
    args = parser.parse_args()
    
    # 验证输入文件
    existing_files = []
    for filepath in args.input_files:
        if Path(filepath).exists():
            existing_files.append(filepath)
        else:
            logger.warning(f"跳过不存在的文件: {filepath}")
    
    if not existing_files:
        logger.error("没有找到有效的输入文件")
        return
    
    logger.info(f"将合并以下文件:")
    for i, filepath in enumerate(existing_files, 1):
        logger.info(f"  {i}. {filepath}")
    
    merge_h5_files(existing_files, args.output, args.symbol, args.interval)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 数据预处理器 - 预处理全量K线数据
生成所有时间周期的数据，提升前端切换速度

功能：
1. 从1分钟数据生成1小时、1天、1月数据
2. 缓存到cache目录，提升加载速度
3. 支持增量更新
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import logging
from datetime import datetime
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('数据预处理.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """数据预处理器"""
    
    def __init__(self):
        self.data_file = Path("K线data/ETHUSDT_1m_2019-11-01_to_2025-06-15.h5")
        self.cache_dir = Path("K线data")  # 🎯 改为K线data文件夹
        self.cache_dir.mkdir(exist_ok=True)
        
        # 时间周期映射
        self.timeframes = {
            '1m': {'freq': '1min', 'cache_file': 'ETHUSDT_1m_processed.pkl'},
            '1h': {'freq': '1h', 'cache_file': 'ETHUSDT_1h_processed.pkl'},
            '1d': {'freq': '1D', 'cache_file': 'ETHUSDT_1d_processed.pkl'},
            '1M': {'freq': '1MS', 'cache_file': 'ETHUSDT_1M_processed.pkl'}  # MS = Month Start
        }
    
    def load_raw_data(self):
        """加载原始1分钟数据"""
        try:
            logger.info("🔄 加载原始1分钟数据...")
            
            if not self.data_file.exists():
                raise FileNotFoundError(f"数据文件不存在: {self.data_file}")
            
            # 读取HDF5文件
            df = pd.read_hdf(self.data_file, key='klines')
            
            # 确保时间索引
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
            elif not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            
            # 确保列名标准化
            column_mapping = {
                'open': 'open',
                'high': 'high', 
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
            
            # 重命名列（如果需要）
            df.columns = [col.lower() for col in df.columns]
            
            logger.info(f"✅ 原始数据加载完成: {len(df)} 条记录")
            logger.info(f"📅 时间范围: {df.index.min()} 至 {df.index.max()}")
            logger.info(f"📊 数据列: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ 加载原始数据失败: {e}")
            raise
    
    def resample_data(self, df, timeframe):
        """重采样数据到指定时间周期"""
        try:
            freq = self.timeframes[timeframe]['freq']
            logger.info(f"🔄 重采样数据到 {timeframe} ({freq})...")
            
            # OHLCV重采样规则
            agg_rules = {
                'open': 'first',
                'high': 'max',
                'low': 'min', 
                'close': 'last',
                'volume': 'sum'
            }
            
            # 执行重采样
            resampled = df.resample(freq).agg(agg_rules)
            
            # 删除空值行
            resampled = resampled.dropna()
            
            logger.info(f"✅ {timeframe} 重采样完成: {len(resampled)} 条记录")
            
            return resampled
            
        except Exception as e:
            logger.error(f"❌ 重采样失败 ({timeframe}): {e}")
            raise
    
    def save_cache(self, df, timeframe):
        """保存缓存数据"""
        try:
            cache_file = self.cache_dir / self.timeframes[timeframe]['cache_file']
            
            # 转换为适合前端的格式
            data_for_frontend = []
            for timestamp, row in df.iterrows():
                data_for_frontend.append({
                    'time': int(timestamp.timestamp()),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume'])
                })
            
            # 保存到pickle文件
            with open(cache_file, 'wb') as f:
                pickle.dump(data_for_frontend, f)
            
            logger.info(f"💾 {timeframe} 数据已缓存: {cache_file}")
            logger.info(f"📊 数据量: {len(data_for_frontend)} 条")
            
        except Exception as e:
            logger.error(f"❌ 保存缓存失败 ({timeframe}): {e}")
            raise
    
    def check_cache_exists(self, timeframe):
        """检查缓存是否存在"""
        cache_file = self.cache_dir / self.timeframes[timeframe]['cache_file']
        return cache_file.exists()
    
    def get_cache_info(self, timeframe):
        """获取缓存信息"""
        cache_file = self.cache_dir / self.timeframes[timeframe]['cache_file']
        if cache_file.exists():
            stat = cache_file.stat()
            return {
                'exists': True,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime)
            }
        return {'exists': False}
    
    def process_all_timeframes(self, force_rebuild=False):
        """处理所有时间周期"""
        try:
            logger.info("🚀 开始预处理所有时间周期数据...")
            
            # 加载原始数据
            raw_data = self.load_raw_data()
            
            # 处理每个时间周期
            for timeframe in self.timeframes.keys():
                logger.info(f"\n📊 处理时间周期: {timeframe}")
                
                # 检查缓存
                if not force_rebuild and self.check_cache_exists(timeframe):
                    cache_info = self.get_cache_info(timeframe)
                    logger.info(f"✅ 缓存已存在: {cache_info['modified']}")
                    continue
                
                # 处理数据
                if timeframe == '1m':
                    # 1分钟数据直接使用原始数据
                    processed_data = raw_data
                else:
                    # 其他周期需要重采样
                    processed_data = self.resample_data(raw_data, timeframe)
                
                # 保存缓存
                self.save_cache(processed_data, timeframe)
            
            logger.info("\n🎉 所有时间周期数据预处理完成！")
            self.print_summary()
            
        except Exception as e:
            logger.error(f"❌ 预处理失败: {e}")
            raise
    
    def print_summary(self):
        """打印处理摘要"""
        logger.info("\n📋 预处理摘要:")
        logger.info("=" * 50)
        
        total_size = 0
        for timeframe, config in self.timeframes.items():
            cache_info = self.get_cache_info(timeframe)
            if cache_info['exists']:
                size_mb = cache_info['size'] / (1024 * 1024)
                total_size += cache_info['size']
                logger.info(f"{timeframe:>4}: {size_mb:>8.2f} MB - {cache_info['modified']}")
            else:
                logger.info(f"{timeframe:>4}: {'缺失':>8}")
        
        logger.info("=" * 50)
        logger.info(f"总计: {total_size / (1024 * 1024):>8.2f} MB")

def main():
    """主函数"""
    try:
        processor = DataPreprocessor()
        
        # 检查是否需要强制重建
        import sys
        force_rebuild = '--force' in sys.argv
        
        if force_rebuild:
            logger.info("🔄 强制重建所有缓存...")
        
        # 处理所有时间周期
        processor.process_all_timeframes(force_rebuild=force_rebuild)
        
        logger.info("\n✅ 数据预处理完成！现在可以快速切换时间周期了。")
        
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 增量数据预处理器 - 智能增量更新K线数据
支持增量更新，大幅提升数据处理效率

功能：
1. 智能检测现有缓存状态
2. 只处理新增数据（增量更新）
3. 支持完全重建模式
4. 数据完整性验证
5. 元数据管理
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import logging
from datetime import datetime
import json
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('增量数据预处理.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IncrementalDataPreprocessor:
    """增量数据预处理器"""
    
    def __init__(self):
        self.data_file = Path("K线data/ETHUSDT_1m_2019-11-01_to_2025-06-15.h5")
        self.cache_dir = Path("K线data")
        self.cache_dir.mkdir(exist_ok=True)
        
        # 时间周期映射
        self.timeframes = {
            '1m': {'freq': '1min', 'cache_file': 'ETHUSDT_1m_processed.pkl'},
            '1h': {'freq': '1h', 'cache_file': 'ETHUSDT_1h_processed.pkl'},
            '1d': {'freq': '1D', 'cache_file': 'ETHUSDT_1d_processed.pkl'},
            '1M': {'freq': '1MS', 'cache_file': 'ETHUSDT_1M_processed.pkl'}
        }
        
        # 元数据文件
        self.metadata_file = self.cache_dir / "cache_metadata.json"
    
    def get_data_hash(self, df):
        """计算数据哈希值用于完整性检查"""
        # 使用数据的关键信息生成哈希
        key_info = f"{len(df)}_{df.index.min()}_{df.index.max()}_{df['close'].sum()}"
        return hashlib.md5(key_info.encode()).hexdigest()
    
    def load_metadata(self):
        """加载缓存元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ 加载元数据失败: {e}")
        return {}
    
    def save_metadata(self, metadata):
        """保存缓存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"💾 元数据已保存: {self.metadata_file}")
        except Exception as e:
            logger.error(f"❌ 保存元数据失败: {e}")
    
    def load_raw_data(self, start_time=None):
        """加载原始数据（支持时间范围过滤）"""
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
            df.columns = [col.lower() for col in df.columns]
            
            # 🎯 增量加载：只加载指定时间之后的数据
            if start_time:
                start_time = pd.to_datetime(start_time)
                df = df[df.index > start_time]
                logger.info(f"📅 增量加载: {start_time} 之后的数据")
            
            logger.info(f"✅ 数据加载完成: {len(df)} 条记录")
            if len(df) > 0:
                logger.info(f"📅 时间范围: {df.index.min()} 至 {df.index.max()}")
                logger.info(f"📊 数据列: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ 加载原始数据失败: {e}")
            raise
    
    def load_existing_cache(self, timeframe):
        """加载现有缓存数据"""
        try:
            cache_file = self.cache_dir / self.timeframes[timeframe]['cache_file']
            
            if not cache_file.exists():
                return None, None
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 检查缓存数据格式
            if isinstance(cache_data, dict) and 'data' in cache_data:
                # 新格式：包含元数据
                return cache_data['data'], cache_data.get('metadata', {})
            else:
                # 旧格式：只有数据
                return cache_data, {}
                
        except Exception as e:
            logger.error(f"❌ 加载现有缓存失败 ({timeframe}): {e}")
            return None, None
    
    def get_cache_last_timestamp(self, timeframe):
        """获取缓存的最后时间戳"""
        existing_data, metadata = self.load_existing_cache(timeframe)
        
        if existing_data and len(existing_data) > 0:
            # 从数据中获取最后时间戳
            last_timestamp = max(item['time'] for item in existing_data)
            return pd.to_datetime(last_timestamp, unit='s')
        
        return None
    
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
    
    def convert_to_frontend_format(self, df):
        """转换为前端格式"""
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
        return data_for_frontend
    
    def merge_data(self, existing_data, new_data):
        """合并现有数据和新数据"""
        if not existing_data:
            return new_data
        
        if not new_data:
            return existing_data
        
        # 合并数据并按时间排序
        all_data = existing_data + new_data
        
        # 去重（基于时间戳）
        seen_times = set()
        unique_data = []
        for item in sorted(all_data, key=lambda x: x['time']):
            if item['time'] not in seen_times:
                unique_data.append(item)
                seen_times.add(item['time'])
        
        logger.info(f"📊 数据合并完成: {len(existing_data)} + {len(new_data)} = {len(unique_data)} 条")
        return unique_data
    
    def save_cache_with_metadata(self, data, timeframe, metadata=None):
        """保存缓存数据（包含元数据）"""
        try:
            cache_file = self.cache_dir / self.timeframes[timeframe]['cache_file']
            
            # 准备元数据
            if metadata is None:
                metadata = {}
            
            metadata.update({
                'timeframe': timeframe,
                'last_updated': datetime.now().isoformat(),
                'data_count': len(data),
                'time_range': {
                    'start': min(item['time'] for item in data) if data else None,
                    'end': max(item['time'] for item in data) if data else None
                }
            })
            
            # 保存数据和元数据
            cache_data = {
                'data': data,
                'metadata': metadata
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.info(f"💾 {timeframe} 数据已缓存: {cache_file}")
            logger.info(f"📊 数据量: {len(data)} 条")
            
        except Exception as e:
            logger.error(f"❌ 保存缓存失败 ({timeframe}): {e}")
            raise

    def process_timeframe_incremental(self, timeframe, force_rebuild=False):
        """🚀 增量处理单个时间周期"""
        try:
            logger.info(f"\n📊 处理时间周期: {timeframe}")

            # 检查现有缓存
            existing_data, existing_metadata = self.load_existing_cache(timeframe)

            if force_rebuild or not existing_data:
                logger.info(f"🔄 完全重建 {timeframe} 缓存...")
                # 完全重建：加载所有数据
                raw_data = self.load_raw_data()

                if timeframe == '1m':
                    processed_data = raw_data
                else:
                    processed_data = self.resample_data(raw_data, timeframe)

                frontend_data = self.convert_to_frontend_format(processed_data)
                self.save_cache_with_metadata(frontend_data, timeframe)

                return len(frontend_data)

            else:
                logger.info(f"🎯 增量更新 {timeframe} 缓存...")

                # 获取最后时间戳
                last_timestamp = self.get_cache_last_timestamp(timeframe)
                logger.info(f"📅 缓存最后时间: {last_timestamp}")

                # 加载新数据
                new_raw_data = self.load_raw_data(start_time=last_timestamp)

                if len(new_raw_data) == 0:
                    logger.info(f"✅ {timeframe} 无新数据，跳过更新")
                    return len(existing_data)

                logger.info(f"📈 发现新数据: {len(new_raw_data)} 条")

                # 处理新数据
                if timeframe == '1m':
                    new_processed_data = new_raw_data
                else:
                    # 对于重采样，需要考虑边界情况
                    # 获取一些重叠数据以确保重采样正确
                    overlap_hours = 24 if timeframe == '1d' else 2
                    overlap_start = last_timestamp - pd.Timedelta(hours=overlap_hours)

                    overlap_raw_data = self.load_raw_data(start_time=overlap_start)
                    new_processed_data = self.resample_data(overlap_raw_data, timeframe)

                    # 只保留真正新的数据
                    new_processed_data = new_processed_data[new_processed_data.index > last_timestamp]

                # 转换格式
                new_frontend_data = self.convert_to_frontend_format(new_processed_data)

                # 合并数据
                merged_data = self.merge_data(existing_data, new_frontend_data)

                # 保存更新后的缓存
                self.save_cache_with_metadata(merged_data, timeframe, existing_metadata)

                return len(merged_data)

        except Exception as e:
            logger.error(f"❌ 处理时间周期失败 ({timeframe}): {e}")
            raise

    def process_all_timeframes_incremental(self, force_rebuild=False):
        """🚀 增量处理所有时间周期"""
        try:
            logger.info("🚀 开始增量预处理所有时间周期数据...")

            # 加载全局元数据
            global_metadata = self.load_metadata()

            # 检查原始数据是否有变化
            raw_data_sample = self.load_raw_data()
            current_data_hash = self.get_data_hash(raw_data_sample)

            if not force_rebuild and global_metadata.get('data_hash') == current_data_hash:
                logger.info("✅ 原始数据无变化，跳过所有更新")
                self.print_summary()
                return

            # 处理每个时间周期
            results = {}
            for timeframe in self.timeframes.keys():
                try:
                    count = self.process_timeframe_incremental(timeframe, force_rebuild)
                    results[timeframe] = count
                except Exception as e:
                    logger.error(f"❌ 处理 {timeframe} 失败: {e}")
                    results[timeframe] = 0

            # 更新全局元数据
            global_metadata.update({
                'last_full_update': datetime.now().isoformat(),
                'data_hash': current_data_hash,
                'timeframe_counts': results
            })
            self.save_metadata(global_metadata)

            logger.info("\n🎉 增量预处理完成！")
            self.print_summary()

        except Exception as e:
            logger.error(f"❌ 增量预处理失败: {e}")
            raise

    def print_summary(self):
        """打印处理摘要"""
        logger.info("\n📋 缓存摘要:")
        logger.info("=" * 60)

        total_size = 0
        for timeframe, config in self.timeframes.items():
            cache_file = self.cache_dir / config['cache_file']
            if cache_file.exists():
                size_mb = cache_file.stat().st_size / (1024 * 1024)
                total_size += cache_file.stat().st_size

                # 获取数据量
                existing_data, metadata = self.load_existing_cache(timeframe)
                count = len(existing_data) if existing_data else 0
                last_updated = metadata.get('last_updated', '未知') if metadata else '未知'

                logger.info(f"{timeframe:>4}: {size_mb:>8.2f} MB | {count:>8,} 条 | {last_updated}")
            else:
                logger.info(f"{timeframe:>4}: {'缺失':>8}")

        logger.info("=" * 60)
        logger.info(f"总计: {total_size / (1024 * 1024):>8.2f} MB")

        # 显示元数据信息
        metadata = self.load_metadata()
        if metadata:
            logger.info(f"\n📊 全局信息:")
            logger.info(f"最后更新: {metadata.get('last_full_update', '未知')}")
            logger.info(f"数据哈希: {metadata.get('data_hash', '未知')[:8]}...")

def main():
    """主函数"""
    try:
        processor = IncrementalDataPreprocessor()

        # 检查命令行参数
        import sys
        force_rebuild = '--force' in sys.argv

        if force_rebuild:
            logger.info("🔄 强制完全重建所有缓存...")
        else:
            logger.info("🎯 智能增量更新模式...")

        # 执行增量处理
        processor.process_all_timeframes_incremental(force_rebuild=force_rebuild)

        logger.info("\n✅ 增量数据预处理完成！现在可以快速切换时间周期了。")

    except Exception as e:
        logger.error(f"❌ 程序执行失败: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理器 - 兼容原始回测引擎的缓存系统
"""

import os
import pickle
import hashlib
from pathlib import Path
from typing import Optional, Any, Dict
import logging
try:
    from core.config import settings
except ImportError:
    from fastapi_backend.core.config import settings

logger = logging.getLogger(__name__)

class CacheManager:
    """缓存管理器 - 完全兼容原始系统"""
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or settings.cache_dir
        self.enabled = settings.cache_enabled
        
    def init(self):
        """初始化缓存目录"""
        if self.enabled:
            self.cache_dir.mkdir(exist_ok=True)
            logger.info(f"✅ 缓存目录初始化: {self.cache_dir}")
            
            # 检查现有缓存文件
            cache_files = list(self.cache_dir.glob("preprocessed_data_*.pkl"))
            logger.info(f"📁 发现 {len(cache_files)} 个缓存文件")
            
            for cache_file in cache_files:
                size_mb = cache_file.stat().st_size / (1024 * 1024)
                logger.info(f"  - {cache_file.name}: {size_mb:.1f} MB")
    
    def get_cache_key(self, data_file: str, start_date: str = None, end_date: str = None) -> str:
        """生成缓存键 - 与原始系统完全兼容"""
        if start_date is None and end_date is None:
            key_string = f"{data_file}_FULL_DATASET"
        else:
            key_string = f"{data_file}_{start_date}_{end_date}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def load_cache(self, cache_key: str) -> Optional[Any]:
        """加载缓存数据 - 与原始系统完全兼容"""
        if not self.enabled:
            return None
            
        cache_file = self.cache_dir / f"preprocessed_data_{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                logger.info(f"✅ 缓存命中: {cache_file.name}")
                return data
            except Exception as e:
                logger.warning(f"⚠️ 缓存加载失败: {e}")
        return None
    
    def save_cache(self, cache_key: str, data: Any):
        """保存缓存数据 - 与原始系统完全兼容"""
        if not self.enabled:
            return
            
        cache_file = self.cache_dir / f"preprocessed_data_{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            size_mb = cache_file.stat().st_size / (1024 * 1024)
            logger.info(f"💾 缓存已保存: {cache_file.name} ({size_mb:.1f} MB)")
        except Exception as e:
            logger.error(f"❌ 缓存保存失败: {e}")
    
    def load_full_dataset_cache(self, data_file: str) -> Optional[Any]:
        """加载全量数据集缓存"""
        cache_key = self.get_cache_key(data_file)
        return self.load_cache(cache_key)
    
    def save_full_dataset_cache(self, data_file: str, data: Any):
        """保存全量数据集缓存"""
        cache_key = self.get_cache_key(data_file)
        self.save_cache(cache_key, data)
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        if not self.enabled:
            return {"enabled": False}
        
        cache_files = list(self.cache_dir.glob("preprocessed_data_*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "enabled": True,
            "cache_dir": str(self.cache_dir),
            "file_count": len(cache_files),
            "total_size_mb": total_size / (1024 * 1024),
            "files": [
                {
                    "name": f.name,
                    "size_mb": f.stat().st_size / (1024 * 1024),
                    "modified": f.stat().st_mtime
                }
                for f in cache_files
            ]
        }
    
    def clear_cache(self):
        """清空缓存"""
        if not self.enabled:
            return
        
        cache_files = list(self.cache_dir.glob("preprocessed_data_*.pkl"))
        for cache_file in cache_files:
            try:
                cache_file.unlink()
                logger.info(f"🗑️ 已删除缓存: {cache_file.name}")
            except Exception as e:
                logger.error(f"❌ 删除缓存失败: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取缓存状态"""
        return {
            "enabled": self.enabled,
            "cache_dir_exists": self.cache_dir.exists() if self.enabled else False,
            "cache_info": self.get_cache_info() if self.enabled else {}
        }
    
    def cleanup(self):
        """清理资源"""
        logger.info("🧹 缓存管理器清理完成")

# 全局缓存管理器实例
cache_manager = CacheManager()

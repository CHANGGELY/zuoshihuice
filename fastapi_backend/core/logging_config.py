#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """设置日志配置"""
    
    # 创建根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建格式器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用轮转文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return root_logger

class PerformanceLogger:
    """性能日志记录器"""
    
    def __init__(self):
        self.logger = logging.getLogger("performance")
    
    def log_backtest_performance(self, params: dict, duration: float, success: bool):
        """记录回测性能"""
        self.logger.info(
            f"回测性能 - "
            f"杠杆: {params.get('leverage', 'N/A')}, "
            f"时间范围: {params.get('startDate', 'N/A')} 到 {params.get('endDate', 'N/A')}, "
            f"耗时: {duration:.2f}s, "
            f"成功: {success}"
        )
    
    def log_cache_performance(self, operation: str, cache_key: str, duration: float):
        """记录缓存性能"""
        self.logger.info(
            f"缓存性能 - "
            f"操作: {operation}, "
            f"键: {cache_key[:20]}..., "
            f"耗时: {duration:.3f}s"
        )
    
    def log_api_performance(self, endpoint: str, method: str, duration: float, status_code: int):
        """记录API性能"""
        self.logger.info(
            f"API性能 - "
            f"{method} {endpoint}, "
            f"状态码: {status_code}, "
            f"耗时: {duration:.3f}s"
        )

# 全局性能日志器
performance_logger = PerformanceLogger()

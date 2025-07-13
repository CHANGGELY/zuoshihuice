#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import os

class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    app_name: str = "永续合约回测系统"
    app_version: str = "2.0.0"
    debug: bool = True

    # 环境配置
    environment: str = "development"  # development, production, testing
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 数据库配置
    database_url: str = "sqlite:///回测结果.db"
    
    # 安全配置
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # CORS配置
    allowed_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    # 文件路径配置
    project_root: Path = Path(__file__).parent.parent.parent.absolute()
    data_file: Path = project_root / "K线data" / "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5"
    backtest_engine: Path = project_root / "backtest_kline_trajectory.py"
    cache_dir: Path = project_root / "cache"
    
    # 回测配置
    max_concurrent_backtests: int = 2
    backtest_timeout: int = 300  # 5分钟超时
    
    # 缓存配置
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1小时
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 全局配置实例
settings = Settings()

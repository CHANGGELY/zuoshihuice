#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控API路由
"""

from fastapi import APIRouter
import psutil
import platform
import time
from datetime import datetime
from pathlib import Path
import logging

try:
    from core.config import settings
    from core.cache import cache_manager
except ImportError:
    from fastapi_backend.core.config import settings
    from fastapi_backend.core.cache import cache_manager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/status", summary="系统状态")
async def get_system_status():
    """获取系统运行状态"""
    try:
        # 系统信息
        system_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        }
        
        # CPU和内存信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        performance_info = {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        }
        
        # 应用信息
        app_info = {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "debug": settings.debug,
            "uptime": time.time() - psutil.Process().create_time()
        }
        
        # 文件状态
        project_root = settings.project_root
        file_status = {
            "backtest_engine_exists": (project_root / settings.backtest_engine.name).exists(),
            "data_file_exists": settings.data_file.exists(),
            "cache_dir_exists": settings.cache_dir.exists(),
            "database_exists": Path(settings.database_url.replace("sqlite:///", "")).exists()
        }
        
        # 缓存状态
        cache_status = cache_manager.get_status()
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "system": system_info,
            "performance": performance_info,
            "application": app_info,
            "files": file_status,
            "cache": cache_status
        }
        
    except Exception as e:
        logger.error(f"❌ 获取系统状态失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/health", summary="健康检查")
async def health_check():
    """详细的健康检查"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # 检查数据库连接
        try:
            from core.database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            health_status["checks"]["database"] = {"status": "healthy", "message": "数据库连接正常"}
        except Exception as e:
            health_status["checks"]["database"] = {"status": "unhealthy", "message": f"数据库连接失败: {e}"}
            health_status["status"] = "unhealthy"
        
        # 检查缓存系统
        try:
            cache_info = cache_manager.get_cache_info()
            health_status["checks"]["cache"] = {
                "status": "healthy", 
                "message": f"缓存系统正常，{cache_info['file_count']}个文件"
            }
        except Exception as e:
            health_status["checks"]["cache"] = {"status": "unhealthy", "message": f"缓存系统异常: {e}"}
            health_status["status"] = "unhealthy"
        
        # 检查核心文件
        backtest_engine = settings.project_root / settings.backtest_engine.name
        if backtest_engine.exists():
            health_status["checks"]["backtest_engine"] = {"status": "healthy", "message": "回测引擎文件存在"}
        else:
            health_status["checks"]["backtest_engine"] = {"status": "unhealthy", "message": "回测引擎文件不存在"}
            health_status["status"] = "unhealthy"
        
        if settings.data_file.exists():
            health_status["checks"]["data_file"] = {"status": "healthy", "message": "数据文件存在"}
        else:
            health_status["checks"]["data_file"] = {"status": "unhealthy", "message": "数据文件不存在"}
            health_status["status"] = "unhealthy"
        
        # 检查系统资源
        memory = psutil.virtual_memory()
        if memory.percent < 90:
            health_status["checks"]["memory"] = {"status": "healthy", "message": f"内存使用率: {memory.percent:.1f}%"}
        else:
            health_status["checks"]["memory"] = {"status": "warning", "message": f"内存使用率过高: {memory.percent:.1f}%"}
        
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent < 90:
            health_status["checks"]["disk"] = {"status": "healthy", "message": f"磁盘使用率: {disk_percent:.1f}%"}
        else:
            health_status["checks"]["disk"] = {"status": "warning", "message": f"磁盘使用率过高: {disk_percent:.1f}%"}
        
        return health_status
        
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/metrics", summary="性能指标")
async def get_metrics():
    """获取详细的性能指标"""
    try:
        # 进程信息
        process = psutil.Process()
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "process": {
                "pid": process.pid,
                "cpu_percent": process.cpu_percent(),
                "memory_info": process.memory_info()._asdict(),
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads(),
                "create_time": process.create_time(),
                "status": process.status()
            },
            "system": {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage('/')._asdict(),
                "boot_time": psutil.boot_time()
            },
            "cache": cache_manager.get_cache_info() if cache_manager.enabled else {"enabled": False}
        }
        
        return {
            "success": True,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"❌ 获取性能指标失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

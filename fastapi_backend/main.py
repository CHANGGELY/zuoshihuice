#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
永续合约回测系统 - FastAPI主应用
高性能异步后端，完美解决Django/Flask崩溃问题
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# 根据运行环境选择导入方式
try:
    # 尝试相对导入（在fastapi_backend目录中运行）
    from api.v1.backtest import router as backtest_router
    from api.v1.simple_backtest import router as simple_backtest_router
    from api.v1.market import router as market_router
    from api.v1.auth import router as auth_router
    from api.v1.websocket import router as websocket_router
    from api.v1.system import router as system_router
    from core.config import settings
    from core.database import init_db
    from core.cache import cache_manager
except ImportError:
    # 回退到绝对导入（在项目根目录运行）
    from fastapi_backend.api.v1.backtest import router as backtest_router
    from fastapi_backend.api.v1.simple_backtest import router as simple_backtest_router
    from fastapi_backend.api.v1.market import router as market_router
    from fastapi_backend.api.v1.auth import router as auth_router
    from fastapi_backend.api.v1.websocket import router as websocket_router
    from fastapi_backend.api.v1.system import router as system_router
    from fastapi_backend.core.config import settings
    from fastapi_backend.core.database import init_db
    from fastapi_backend.core.cache import cache_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fastapi_backend.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("🚀 FastAPI 永续合约回测系统启动中...")
    
    # 初始化数据库
    init_db()
    logger.info("✅ 数据库初始化完成")
    
    # 初始化缓存系统
    cache_manager.init()
    logger.info("✅ 缓存系统初始化完成")
    
    # 检查核心文件
    backtest_engine = project_root / "backtest_kline_trajectory.py"
    data_file = project_root / "K线data" / "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5"
    
    if not backtest_engine.exists():
        logger.error(f"❌ 回测引擎不存在: {backtest_engine}")
    else:
        logger.info(f"✅ 回测引擎: {backtest_engine}")
    
    if not data_file.exists():
        logger.error(f"❌ 数据文件不存在: {data_file}")
    else:
        logger.info(f"✅ 数据文件: {data_file}")
    
    logger.info("🎉 系统启动完成！")
    
    yield
    
    # 关闭时清理
    logger.info("🛑 FastAPI 系统正在关闭...")
    cache_manager.cleanup()
    logger.info("👋 系统已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="永续合约回测系统",
    description="专业的量化交易回测平台 - FastAPI版本",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 导入自定义中间件
try:
    from core.middleware import (
        PerformanceMiddleware,
        RequestLoggingMiddleware,
        ErrorHandlingMiddleware,
        SecurityMiddleware
    )
except ImportError:
    from fastapi_backend.core.middleware import (
        PerformanceMiddleware,
        RequestLoggingMiddleware,
        ErrorHandlingMiddleware,
        SecurityMiddleware
    )

# 添加中间件（顺序很重要）
app.add_middleware(ErrorHandlingMiddleware)  # 最外层：错误处理
app.add_middleware(PerformanceMiddleware)    # 性能监控
app.add_middleware(RequestLoggingMiddleware) # 请求日志
app.add_middleware(SecurityMiddleware)       # 安全头
app.add_middleware(GZipMiddleware, minimum_size=1000)  # 压缩

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(backtest_router, prefix="/api/v1/backtest", tags=["回测"])
app.include_router(simple_backtest_router, prefix="/api/v1/simple-backtest", tags=["简化回测"])
app.include_router(market_router, prefix="/api/v1/market", tags=["市场数据"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(system_router, prefix="/api/v1/system", tags=["系统监控"])
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

@app.get("/", summary="根路径")
async def root():
    """根路径，返回系统信息"""
    return {
        "message": "永续合约回测系统 FastAPI 后端",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查接口"""
    backtest_engine = project_root / "backtest_kline_trajectory.py"
    data_file = project_root / "K线data" / "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5"
    
    return {
        "status": "healthy",
        "backtest_engine_exists": backtest_engine.exists(),
        "data_file_exists": data_file.exists(),
        "cache_status": cache_manager.get_status()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

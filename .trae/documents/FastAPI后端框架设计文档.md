# FastAPI 后端框架设计文档

## 1. 项目架构概述

### 1.1 技术栈选择
- **FastAPI 0.104+**: 高性能异步Web框架
- **SQLAlchemy 2.0+**: 异步ORM，支持类型提示
- **Pydantic 2.0+**: 数据验证和序列化
- **asyncpg**: 高性能PostgreSQL异步驱动
- **Redis**: 缓存和会话存储
- **Celery**: 异步任务队列
- **WebSocket**: 实时数据推送

### 1.2 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py              # 配置管理
│   ├── dependencies.py        # 依赖注入
│   ├── middleware.py          # 中间件
│   ├── exceptions.py          # 异常处理
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py        # 数据库连接
│   │   ├── redis.py           # Redis连接
│   │   ├── security.py        # 安全认证
│   │   ├── cache.py           # 缓存管理
│   │   └── websocket.py       # WebSocket管理
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py            # 基础模型
│   │   ├── kline.py           # K线数据模型
│   │   ├── backtest.py        # 回测模型
│   │   ├── trade.py           # 交易记录模型
│   │   └── user.py            # 用户模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py            # 基础Schema
│   │   ├── kline.py           # K线数据Schema
│   │   ├── backtest.py        # 回测Schema
│   │   ├── trade.py           # 交易Schema
│   │   └── response.py        # 响应Schema
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py      # 路由汇总
│   │   │   ├── kline.py       # K线数据API
│   │   │   ├── backtest.py    # 回测API
│   │   │   ├── strategy.py    # 策略API
│   │   │   ├── monitor.py     # 监控API
│   │   │   └── websocket.py   # WebSocket API
│   ├── services/
│   │   ├── __init__.py
│   │   ├── kline_service.py   # K线数据服务
│   │   ├── backtest_service.py # 回测服务
│   │   ├── strategy_service.py # 策略服务
│   │   ├── cache_service.py   # 缓存服务
│   │   └── notification_service.py # 通知服务
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py            # 基础仓储
│   │   ├── kline_repository.py # K线数据仓储
│   │   ├── backtest_repository.py # 回测仓储
│   │   └── trade_repository.py # 交易仓储
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py      # Celery配置
│   │   ├── backtest_tasks.py  # 回测任务
│   │   └── data_tasks.py      # 数据处理任务
│   └── utils/
│       ├── __init__.py
│       ├── logger.py          # 日志工具
│       ├── validators.py      # 验证工具
│       ├── formatters.py      # 格式化工具
│       └── decorators.py      # 装饰器
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # 测试配置
│   ├── test_api/
│   ├── test_services/
│   └── test_repositories/
├── alembic/                  # 数据库迁移
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── requirements.txt
├── requirements-dev.txt
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

## 2. 核心组件设计

### 2.1 应用入口 (main.py)

```python
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.config import settings
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis
from app.api.v1.router import api_router
from app.middleware import (
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware
)
from app.exceptions import (
    ValidationException,
    BusinessException,
    validation_exception_handler,
    business_exception_handler
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    await init_db()
    await init_redis()
    logging.info("应用启动完成")
    
    yield
    
    # 关闭时清理
    await close_db()
    await close_redis()
    logging.info("应用关闭完成")

def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(
        title="量化交易回测系统API",
        description="高性能量化交易策略回测和分析平台",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    # 注册异常处理器
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(BusinessException, business_exception_handler)
    
    # 注册路由
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {"status": "healthy", "version": "1.0.0"}
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
        log_level="debug" if settings.DEBUG else "info"
    )
```

### 2.2 配置管理 (config.py)

```python
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    DEBUG: bool = False
    SECRET_KEY: str
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 数据库配置
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # JWT配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 限流配置
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_PATH: str = "uploads"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # 回测配置
    MAX_BACKTEST_DURATION_DAYS: int = 365 * 2  # 最大回测时长2年
    MAX_CONCURRENT_BACKTESTS: int = 5
    BACKTEST_TIMEOUT_MINUTES: int = 30
    
    # WebSocket配置
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    WEBSOCKET_MAX_CONNECTIONS: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 2.3 数据库连接 (core/database.py)

```python
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from app.config import settings

class Base(DeclarativeBase):
    """数据库模型基类"""
    pass

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = None
        self.async_session = None
    
    async def init_db(self):
        """初始化数据库连接"""
        self.engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
            pool_recycle=settings.DATABASE_POOL_RECYCLE
        )
        
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logging.info("数据库连接初始化完成")
    
    async def close_db(self):
        """关闭数据库连接"""
        if self.engine:
            await self.engine.dispose()
            logging.info("数据库连接已关闭")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话"""
        if not self.async_session:
            raise RuntimeError("数据库未初始化")
        
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def execute_raw_sql(self, query: str, params: dict = None):
        """执行原生SQL"""
        async with self.engine.begin() as conn:
            result = await conn.execute(query, params or {})
            return result.fetchall()

# 全局数据库管理器
db_manager = DatabaseManager()

# 便捷函数
async def init_db():
    await db_manager.init_db()

async def close_db():
    await db_manager.close_db()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.get_session() as session:
        yield session
```

### 2.4 Redis连接 (core/redis.py)

```python
import redis.asyncio as redis
from typing import Optional, Any, Union
import json
import pickle
import logging

from app.config import settings

class RedisManager:
    """Redis管理器"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
    
    async def init_redis(self):
        """初始化Redis连接"""
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False,  # 支持二进制数据
            max_connections=20
        )
        
        # 测试连接
        await self.redis_client.ping()
        logging.info("Redis连接初始化完成")
    
    async def close_redis(self):
        """关闭Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
            logging.info("Redis连接已关闭")
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serialize: str = "json"
    ) -> bool:
        """设置缓存值"""
        if not self.redis_client:
            raise RuntimeError("Redis未初始化")
        
        # 序列化数据
        if serialize == "json":
            serialized_value = json.dumps(value, ensure_ascii=False)
        elif serialize == "pickle":
            serialized_value = pickle.dumps(value)
        else:
            serialized_value = str(value)
        
        ttl = ttl or settings.REDIS_CACHE_TTL
        return await self.redis_client.setex(key, ttl, serialized_value)
    
    async def get(
        self, 
        key: str, 
        default: Any = None,
        deserialize: str = "json"
    ) -> Any:
        """获取缓存值"""
        if not self.redis_client:
            raise RuntimeError("Redis未初始化")
        
        value = await self.redis_client.get(key)
        if value is None:
            return default
        
        # 反序列化数据
        try:
            if deserialize == "json":
                return json.loads(value)
            elif deserialize == "pickle":
                return pickle.loads(value)
            else:
                return value.decode('utf-8')
        except Exception as e:
            logging.error(f"反序列化缓存数据失败: {e}")
            return default
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.redis_client:
            raise RuntimeError("Redis未初始化")
        
        return bool(await self.redis_client.delete(key))
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.redis_client:
            raise RuntimeError("Redis未初始化")
        
        return bool(await self.redis_client.exists(key))
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        if not self.redis_client:
            raise RuntimeError("Redis未初始化")
        
        return await self.redis_client.incrby(key, amount)
    
    async def set_hash(self, key: str, mapping: dict, ttl: Optional[int] = None):
        """设置哈希表"""
        if not self.redis_client:
            raise RuntimeError("Redis未初始化")
        
        await self.redis_client.hset(key, mapping=mapping)
        if ttl:
            await self.redis_client.expire(key, ttl)
    
    async def get_hash(self, key: str, field: Optional[str] = None):
        """获取哈希表"""
        if not self.redis_client:
            raise RuntimeError("Redis未初始化")
        
        if field:
            return await self.redis_client.hget(key, field)
        else:
            return await self.redis_client.hgetall(key)

# 全局Redis管理器
redis_manager = RedisManager()

# 便捷函数
async def init_redis():
    await redis_manager.init_redis()

async def close_redis():
    await redis_manager.close_redis()

def get_redis() -> RedisManager:
    return redis_manager
```

## 3. API路由设计

### 3.1 路由汇总 (api/v1/router.py)

```python
from fastapi import APIRouter

from app.api.v1 import (
    kline,
    backtest,
    strategy,
    monitor,
    websocket
)

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(
    kline.router, 
    prefix="/kline", 
    tags=["K线数据"]
)

api_router.include_router(
    backtest.router, 
    prefix="/backtest", 
    tags=["回测"]
)

api_router.include_router(
    strategy.router, 
    prefix="/strategy", 
    tags=["策略"]
)

api_router.include_router(
    monitor.router, 
    prefix="/monitor", 
    tags=["监控"]
)

api_router.include_router(
    websocket.router, 
    prefix="/ws", 
    tags=["WebSocket"]
)
```

### 3.2 K线数据API (api/v1/kline.py)

```python
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime, date

from app.schemas.kline import (
    KlineDataResponse,
    KlineDataCreate,
    KlineDataQuery,
    KlineUploadResponse
)
from app.schemas.response import StandardResponse, PaginatedResponse
from app.services.kline_service import KlineService
from app.dependencies import get_kline_service
from app.utils.validators import validate_date_range

router = APIRouter()

@router.get(
    "/{symbol}",
    response_model=StandardResponse[PaginatedResponse[KlineDataResponse]],
    summary="获取K线数据",
    description="根据交易对、时间框架和时间范围获取K线数据"
)
async def get_kline_data(
    symbol: str,
    timeframe: str = Query(..., description="时间框架 (1m, 5m, 15m, 1h, 4h, 1d)"),
    start_date: datetime = Query(..., description="开始时间"),
    end_date: datetime = Query(..., description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(1000, ge=1, le=10000, description="每页数量"),
    kline_service: KlineService = Depends(get_kline_service)
):
    """获取K线数据"""
    
    # 验证日期范围
    validate_date_range(start_date, end_date)
    
    # 构建查询参数
    query = KlineDataQuery(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size
    )
    
    # 获取数据
    result = await kline_service.get_kline_data(query)
    
    return StandardResponse(
        success=True,
        data=result,
        message="K线数据获取成功"
    )

@router.post(
    "/upload",
    response_model=StandardResponse[KlineUploadResponse],
    summary="上传K线数据",
    description="批量上传K线数据到数据库"
)
async def upload_kline_data(
    kline_data: List[KlineDataCreate],
    kline_service: KlineService = Depends(get_kline_service)
):
    """上传K线数据"""
    
    if not kline_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="K线数据不能为空"
        )
    
    if len(kline_data) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="单次上传数据量不能超过10000条"
        )
    
    # 上传数据
    result = await kline_service.upload_kline_data(kline_data)
    
    return StandardResponse(
        success=True,
        data=result,
        message=f"成功上传{result.uploaded_count}条K线数据"
    )

@router.get(
    "/symbols",
    response_model=StandardResponse[List[str]],
    summary="获取交易对列表",
    description="获取系统中所有可用的交易对"
)
async def get_symbols(
    kline_service: KlineService = Depends(get_kline_service)
):
    """获取交易对列表"""
    
    symbols = await kline_service.get_available_symbols()
    
    return StandardResponse(
        success=True,
        data=symbols,
        message="交易对列表获取成功"
    )

@router.get(
    "/{symbol}/latest",
    response_model=StandardResponse[Optional[datetime]],
    summary="获取最新数据时间",
    description="获取指定交易对和时间框架的最新数据时间戳"
)
async def get_latest_timestamp(
    symbol: str,
    timeframe: str = Query(..., description="时间框架"),
    kline_service: KlineService = Depends(get_kline_service)
):
    """获取最新数据时间"""
    
    timestamp = await kline_service.get_latest_timestamp(symbol, timeframe)
    
    return StandardResponse(
        success=True,
        data=timestamp,
        message="最新时间戳获取成功"
    )
```

### 3.3 回测API (api/v1/backtest.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
from uuid import UUID

from app.schemas.backtest import (
    BacktestRequest,
    BacktestResponse,
    BacktestStatus,
    BacktestResult,
    BacktestProgress
)
from app.schemas.response import StandardResponse, PaginatedResponse
from app.services.backtest_service import BacktestService
from app.dependencies import get_backtest_service
from app.tasks.backtest_tasks import run_backtest_task

router = APIRouter()

@router.post(
    "/run",
    response_model=StandardResponse[BacktestResponse],
    summary="启动回测",
    description="提交回测任务并异步执行"
)
async def run_backtest(
    request: BacktestRequest,
    background_tasks: BackgroundTasks,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """启动回测"""
    
    # 验证回测参数
    await backtest_service.validate_backtest_request(request)
    
    # 创建回测任务
    backtest_id = await backtest_service.create_backtest_task(request)
    
    # 提交异步任务
    background_tasks.add_task(
        run_backtest_task.delay,
        str(backtest_id),
        request.dict()
    )
    
    return StandardResponse(
        success=True,
        data=BacktestResponse(
            backtest_id=backtest_id,
            status="PENDING",
            message="回测任务已提交，正在排队执行"
        ),
        message="回测任务创建成功"
    )

@router.get(
    "/{backtest_id}/status",
    response_model=StandardResponse[BacktestStatus],
    summary="获取回测状态",
    description="查询回测任务的执行状态和进度"
)
async def get_backtest_status(
    backtest_id: UUID,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """获取回测状态"""
    
    status = await backtest_service.get_backtest_status(backtest_id)
    
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回测任务不存在"
        )
    
    return StandardResponse(
        success=True,
        data=status,
        message="回测状态获取成功"
    )

@router.get(
    "/{backtest_id}/result",
    response_model=StandardResponse[BacktestResult],
    summary="获取回测结果",
    description="获取已完成回测的详细结果"
)
async def get_backtest_result(
    backtest_id: UUID,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """获取回测结果"""
    
    result = await backtest_service.get_backtest_result(backtest_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回测结果不存在"
        )
    
    return StandardResponse(
        success=True,
        data=result,
        message="回测结果获取成功"
    )

@router.get(
    "/history",
    response_model=StandardResponse[PaginatedResponse[BacktestResult]],
    summary="获取回测历史",
    description="分页获取历史回测记录"
)
async def get_backtest_history(
    strategy_name: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """获取回测历史"""
    
    history = await backtest_service.get_backtest_history(
        strategy_name=strategy_name,
        page=page,
        page_size=page_size
    )
    
    return StandardResponse(
        success=True,
        data=history,
        message="回测历史获取成功"
    )

@router.delete(
    "/{backtest_id}",
    response_model=StandardResponse[bool],
    summary="删除回测",
    description="删除指定的回测任务和结果"
)
async def delete_backtest(
    backtest_id: UUID,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """删除回测"""
    
    success = await backtest_service.delete_backtest(backtest_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回测任务不存在"
        )
    
    return StandardResponse(
        success=True,
        data=True,
        message="回测删除成功"
    )

@router.post(
    "/{backtest_id}/stop",
    response_model=StandardResponse[bool],
    summary="停止回测",
    description="停止正在执行的回测任务"
)
async def stop_backtest(
    backtest_id: UUID,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """停止回测"""
    
    success = await backtest_service.stop_backtest(backtest_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法停止回测任务"
        )
    
    return StandardResponse(
        success=True,
        data=True,
        message="回测停止成功"
    )
```

## 4. WebSocket实时通信

### 4.1 WebSocket管理器 (core/websocket.py)

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Optional, Any
import json
import asyncio
import logging
from uuid import UUID, uuid4
from datetime import datetime

from app.config import settings

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接: {connection_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # 订阅关系: {topic: {connection_id}}
        self.subscriptions: Dict[str, Set[str]] = {}
        
        # 连接元数据: {connection_id: metadata}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # 心跳任务
        self.heartbeat_task: Optional[asyncio.Task] = None
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        """接受WebSocket连接"""
        await websocket.accept()
        
        connection_id = client_id or str(uuid4())
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "connected_at": datetime.now(),
            "last_ping": datetime.now(),
            "subscriptions": set()
        }
        
        logging.info(f"WebSocket连接建立: {connection_id}")
        
        # 启动心跳检测
        if not self.heartbeat_task:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """断开WebSocket连接"""
        if connection_id in self.active_connections:
            # 清理订阅关系
            for topic in list(self.subscriptions.keys()):
                self.subscriptions[topic].discard(connection_id)
                if not self.subscriptions[topic]:
                    del self.subscriptions[topic]
            
            # 清理连接
            del self.active_connections[connection_id]
            del self.connection_metadata[connection_id]
            
            logging.info(f"WebSocket连接断开: {connection_id}")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """发送个人消息"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logging.error(f"发送消息失败: {e}")
                await self.disconnect(connection_id)
    
    async def broadcast_to_topic(self, message: dict, topic: str):
        """向主题订阅者广播消息"""
        if topic in self.subscriptions:
            disconnected_connections = []
            
            for connection_id in self.subscriptions[topic]:
                if connection_id in self.active_connections:
                    websocket = self.active_connections[connection_id]
                    try:
                        await websocket.send_text(json.dumps(message, ensure_ascii=False))
                    except Exception as e:
                        logging.error(f"广播消息失败: {e}")
                        disconnected_connections.append(connection_id)
            
            # 清理断开的连接
            for connection_id in disconnected_connections:
                await self.disconnect(connection_id)
    
    async def subscribe(self, connection_id: str, topic: str):
        """订阅主题"""
        if connection_id in self.active_connections:
            if topic not in self.subscriptions:
                self.subscriptions[topic] = set()
            
            self.subscriptions[topic].add(connection_id)
            self.connection_metadata[connection_id]["subscriptions"].add(topic)
            
            logging.info(f"连接 {connection_id} 订阅主题: {topic}")
    
    async def unsubscribe(self, connection_id: str, topic: str):
        """取消订阅"""
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(connection_id)
            if not self.subscriptions[topic]:
                del self.subscriptions[topic]
        
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]["subscriptions"].discard(topic)
        
        logging.info(f"连接 {connection_id} 取消订阅主题: {topic}")
    
    async def _heartbeat_loop(self):
        """心跳检测循环"""
        while True:
            try:
                await asyncio.sleep(settings.WEBSOCKET_HEARTBEAT_INTERVAL)
                
                current_time = datetime.now()
                disconnected_connections = []
                
                for connection_id, websocket in self.active_connections.items():
                    try:
                        # 发送心跳
                        await websocket.send_text(json.dumps({
                            "type": "heartbeat",
                            "timestamp": current_time.isoformat()
                        }))
                        
                        # 更新最后心跳时间
                        self.connection_metadata[connection_id]["last_ping"] = current_time
                        
                    except Exception:
                        disconnected_connections.append(connection_id)
                
                # 清理断开的连接
                for connection_id in disconnected_connections:
                    await self.disconnect(connection_id)
                
            except Exception as e:
                logging.error(f"心跳检测错误: {e}")
    
    def get_connection_count(self) -> int:
        """获取活跃连接数"""
        return len(self.active_connections)
    
    def get_topic_subscribers(self, topic: str) -> int:
        """获取主题订阅者数量"""
        return len(self.subscriptions.get(topic, set()))

# 全局连接管理器
connection_manager = ConnectionManager()
```

### 4.2 WebSocket API (api/v1/websocket.py)

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
import logging
from typing import Dict, Any

from app.core.websocket import connection_manager
from app.services.backtest_service import BacktestService
from app.dependencies import get_backtest_service

router = APIRouter()

@router.websocket("/backtest/{backtest_id}")
async def backtest_websocket(
    websocket: WebSocket,
    backtest_id: str,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """回测实时监控WebSocket"""
    connection_id = await connection_manager.connect(websocket)
    
    try:
        # 订阅回测进度主题
        topic = f"backtest_progress_{backtest_id}"
        await connection_manager.subscribe(connection_id, topic)
        
        # 发送连接成功消息
        await connection_manager.send_personal_message({
            "type": "connected",
            "backtest_id": backtest_id,
            "connection_id": connection_id
        }, connection_id)
        
        # 发送当前状态
        current_status = await backtest_service.get_backtest_status(backtest_id)
        if current_status:
            await connection_manager.send_personal_message({
                "type": "status_update",
                "data": current_status.dict()
            }, connection_id)
        
        # 监听客户端消息
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await handle_websocket_message(connection_id, message, backtest_service)
            
    except WebSocketDisconnect:
        await connection_manager.disconnect(connection_id)
        logging.info(f"回测WebSocket断开: {backtest_id}")
    except Exception as e:
        logging.error(f"回测WebSocket错误: {e}")
        await connection_manager.disconnect(connection_id)

@router.websocket("/monitor")
async def monitor_websocket(websocket: WebSocket):
    """系统监控WebSocket"""
    connection_id = await connection_manager.connect(websocket)
    
    try:
        # 订阅系统监控主题
        await connection_manager.subscribe(connection_id, "system_monitor")
        
        # 发送连接成功消息
        await connection_manager.send_personal_message({
            "type": "connected",
            "connection_id": connection_id
        }, connection_id)
        
        # 监听客户端消息
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await connection_manager.send_personal_message({
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }, connection_id)
            
    except WebSocketDisconnect:
        await connection_manager.disconnect(connection_id)
        logging.info("监控WebSocket断开")
    except Exception as e:
        logging.error(f"监控WebSocket错误: {e}")
        await connection_manager.disconnect(connection_id)

async def handle_websocket_message(
    connection_id: str, 
    message: Dict[str, Any],
    backtest_service: BacktestService
):
    """处理WebSocket消息"""
    message_type = message.get("type")
    
    if message_type == "ping":
        await connection_manager.send_personal_message({
            "type": "pong",
            "timestamp": message.get("timestamp")
        }, connection_id)
    
    elif message_type == "subscribe":
        topic = message.get("topic")
        if topic:
            await connection_manager.subscribe(connection_id, topic)
            await connection_manager.send_personal_message({
                "type": "subscribed",
                "topic": topic
            }, connection_id)
    
    elif message_type == "unsubscribe":
        topic = message.get("topic")
        if topic:
            await connection_manager.unsubscribe(connection_id, topic)
            await connection_manager.send_personal_message({
                "type": "unsubscribed",
                "topic": topic
            }, connection_id)
    
    else:
        await connection_manager.send_personal_message({
            "type": "error",
            "message": f"未知消息类型: {message_type}"
        }, connection_id)

# 广播回测进度更新
async def broadcast_backtest_progress(backtest_id: str, progress_data: Dict[str, Any]):
    """广播回测进度更新"""
    topic = f"backtest_progress_{backtest_id}"
    message = {
        "type": "progress_update",
        "backtest_id": backtest_id,
        "data": progress_data
    }
    await connection_manager.broadcast_to_topic(message, topic)

# 广播系统监控数据
async def broadcast_system_metrics(metrics_data: Dict[str, Any]):
    """广播系统监控数据"""
    message = {
        "type": "system_metrics",
        "data": metrics_data
    }
    await connection_manager.broadcast_to_topic(message, "system_monitor")
```

## 5. 异步任务处理

### 5.1 Celery配置 (tasks/celery_app.py)

```python
from celery import Celery
from app.config import settings

# 创建Celery应用
celery_app = Celery(
    "quant_trading",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.backtest_tasks",
        "app.tasks.data_tasks"
    ]
)

# Celery配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟超时
    task_soft_time_limit=25 * 60,  # 25分钟软超时
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 任务路由配置
celery_app.conf.task_routes = {
    "app.tasks.backtest_tasks.*": {"queue": "backtest"},
    "app.tasks.data_tasks.*": {"queue": "data"},
}
```

### 5.2 回测任务 (tasks/backtest_tasks.py)

```python
from celery import current_task
from typing import Dict, Any
import asyncio
import logging
from uuid import UUID

from app.tasks.celery_app import celery_app
from app.services.backtest_service import BacktestService
from app.core.database import db_manager
from app.api.v1.websocket import broadcast_backtest_progress

@celery_app.task(bind=True)
def run_backtest_task(self, backtest_id: str, backtest_params: Dict[str, Any]):
    """执行回测任务"""
    
    async def _run_backtest():
        try:
            # 初始化数据库连接
            await db_manager.init_db()
            
            # 创建服务实例
            backtest_service = BacktestService()
            
            # 更新任务状态为运行中
            await backtest_service.update_backtest_status(
                UUID(backtest_id), 
                "RUNNING",
                "回测正在执行中"
            )
            
            # 广播状态更新
            await broadcast_backtest_progress(backtest_id, {
                "status": "RUNNING",
                "progress": 0,
                "message": "回测开始执行"
            })
            
            # 执行回测
            result = await backtest_service.execute_backtest(
                UUID(backtest_id),
                backtest_params,
                progress_callback=lambda progress, message: asyncio.create_task(
                    broadcast_backtest_progress(backtest_id, {
                        "status": "RUNNING",
                        "progress": progress,
                        "message": message
                    })
                )
            )
            
            # 更新任务状态为完成
            await backtest_service.update_backtest_status(
                UUID(backtest_id),
                "COMPLETED",
                "回测执行完成"
            )
            
            # 广播完成状态
            await broadcast_backtest_progress(backtest_id, {
                "status": "COMPLETED",
                "progress": 100,
                "message": "回测执行完成",
                "result": result.dict() if result else None
            })
            
            return {"success": True, "result": result.dict() if result else None}
            
        except Exception as e:
            logging.error(f"回测任务执行失败: {e}")
            
            # 更新任务状态为失败
            await backtest_service.update_backtest_status(
                UUID(backtest_id),
                "FAILED",
                f"回测执行失败: {str(e)}"
            )
            
            # 广播失败状态
            await broadcast_backtest_progress(backtest_id, {
                "status": "FAILED",
                "progress": 0,
                "message": f"回测执行失败: {str(e)}"
            })
            
            raise
        
        finally:
            # 关闭数据库连接
            await db_manager.close_db()
    
    # 运行异步任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run_backtest())
    finally:
        loop.close()

@celery_app.task
def cleanup_expired_backtests():
    """清理过期的回测任务"""
    
    async def _cleanup():
        await db_manager.init_db()
        try:
            backtest_service = BacktestService()
            cleaned_count = await backtest_service.cleanup_expired_backtests()
            logging.info(f"清理了 {cleaned_count} 个过期回测任务")
            return cleaned_count
        finally:
            await db_manager.close_db()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_cleanup())
    finally:
        loop.close()
```

## 6. 部署配置

### 6.1 Docker配置

```dockerfile
# Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # FastAPI应用
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/quant_trading
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      - postgres
      - redis
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  # Celery Worker
  celery-worker:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info --queues=backtest,data
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/quant_trading
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # Celery Beat (定时任务)
  celery-beat:
    build: .
    command: celery -A app.tasks.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/quant_trading
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # PostgreSQL数据库
  postgres:
    image: timescale/timescaledb:latest-pg15
    environment:
      - POSTGRES_DB=quant_trading
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Redis缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

通过以上设计，我们构建了一个高性能、可扩展的FastAPI后端框架，具备完整的API设计、异步任务处理、实时通信和部署配置，为量化交易回测系统提供了坚实的技术基础。
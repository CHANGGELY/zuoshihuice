# PostgreSQL + TimescaleDB 数据库环境搭建指南

## 1. 环境概述

本指南专为量化交易回测系统设计，重点优化时序数据的存储和查询性能。

### 1.1 技术栈选择

* **PostgreSQL 15+**: 企业级关系数据库，ACID保证

* **TimescaleDB 2.11+**: PostgreSQL时序数据扩展，专为时间序列优化

* **连接池**: PgBouncer用于高并发连接管理

* **监控**: pg\_stat\_statements + TimescaleDB监控工具

### 1.2 系统要求

* **内存**: 最低8GB，推荐16GB+

* **存储**: SSD硬盘，至少100GB可用空间

* **CPU**: 4核心以上，支持并行查询

* **网络**: 低延迟网络环境

## 2. 安装配置步骤

### 2.1 PostgreSQL 安装

#### Windows 环境

```powershell
# 下载PostgreSQL 15官方安装包
# https://www.postgresql.org/download/windows/

# 或使用Chocolatey安装
choco install postgresql --version=15.4

# 设置环境变量
$env:PGDATA = "C:\PostgreSQL\15\data"
$env:PATH += ";C:\PostgreSQL\15\bin"
```

#### Linux 环境

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql-15 postgresql-contrib-15

# CentOS/RHEL
sudo yum install postgresql15-server postgresql15-contrib
sudo postgresql-15-setup initdb
sudo systemctl enable postgresql-15
sudo systemctl start postgresql-15
```

### 2.2 TimescaleDB 扩展安装

#### Windows

```powershell
# 下载TimescaleDB Windows安装包
# https://docs.timescale.com/install/latest/self-hosted/installation-windows/

# 安装后修改postgresql.conf
# shared_preload_libraries = 'timescaledb'

# 重启PostgreSQL服务
Restart-Service postgresql-x64-15
```

#### Linux

```bash
# 添加TimescaleDB仓库
echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -

# 安装TimescaleDB
sudo apt update
sudo apt install timescaledb-2-postgresql-15

# 配置TimescaleDB
sudo timescaledb-tune

# 重启PostgreSQL
sudo systemctl restart postgresql
```

### 2.3 数据库初始化

```sql
-- 连接到PostgreSQL
psql -U postgres

-- 创建数据库
CREATE DATABASE quant_trading;

-- 连接到新数据库
\c quant_trading;

-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 验证安装
SELECT timescaledb_version();
```

## 3. 数据表结构设计

### 3.1 K线数据表 (时序表)

```sql
-- 创建K线数据表
CREATE TABLE kline_data (
    id BIGSERIAL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open DECIMAL(20,8) NOT NULL,
    high DECIMAL(20,8) NOT NULL,
    low DECIMAL(20,8) NOT NULL,
    close DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 转换为时序表（核心优化）
SELECT create_hypertable('kline_data', 'timestamp', 
    chunk_time_interval => INTERVAL '1 day',
    create_default_indexes => FALSE
);

-- 创建复合索引（查询优化）
CREATE INDEX idx_kline_symbol_timeframe_timestamp 
ON kline_data (symbol, timeframe, timestamp DESC);

CREATE INDEX idx_kline_timestamp_symbol 
ON kline_data (timestamp DESC, symbol);

-- 创建部分索引（常用查询优化）
CREATE INDEX idx_kline_eth_1h 
ON kline_data (timestamp DESC) 
WHERE symbol = 'ETH-USDC' AND timeframe = '1h';
```

### 3.2 交易记录表 (时序表)

```sql
-- 创建交易记录表
CREATE TABLE trade_records (
    id BIGSERIAL,
    backtest_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL, -- 'long' or 'short'
    action VARCHAR(10) NOT NULL, -- 'open' or 'close'
    quantity DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    fee DECIMAL(20,8) NOT NULL,
    pnl DECIMAL(20,8),
    balance_after DECIMAL(20,8) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 转换为时序表
SELECT create_hypertable('trade_records', 'timestamp',
    chunk_time_interval => INTERVAL '7 days'
);

-- 创建索引
CREATE INDEX idx_trade_backtest_timestamp 
ON trade_records (backtest_id, timestamp DESC);

CREATE INDEX idx_trade_symbol_timestamp 
ON trade_records (symbol, timestamp DESC);
```

### 3.3 回测结果表 (常规表)

```sql
-- 创建回测结果表
CREATE TABLE backtest_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_name VARCHAR(100) NOT NULL,
    parameters JSONB NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_balance DECIMAL(20,8) NOT NULL,
    final_balance DECIMAL(20,8) NOT NULL,
    total_return DECIMAL(10,4) NOT NULL,
    max_drawdown DECIMAL(10,4) NOT NULL,
    sharpe_ratio DECIMAL(10,4),
    total_trades INTEGER NOT NULL,
    win_rate DECIMAL(5,2) NOT NULL,
    is_liquidated BOOLEAN DEFAULT FALSE,
    execution_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_backtest_strategy_created 
ON backtest_results (strategy_name, created_at DESC);

CREATE INDEX idx_backtest_performance 
ON backtest_results (total_return DESC, sharpe_ratio DESC);

-- 创建GIN索引用于JSONB参数查询
CREATE INDEX idx_backtest_parameters 
ON backtest_results USING GIN (parameters);
```

### 3.4 实时指标表 (时序表)

```sql
-- 创建实时指标表
CREATE TABLE realtime_metrics (
    timestamp TIMESTAMPTZ NOT NULL,
    backtest_id UUID NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(20,8) NOT NULL,
    metadata JSONB
);

-- 转换为时序表
SELECT create_hypertable('realtime_metrics', 'timestamp',
    chunk_time_interval => INTERVAL '1 hour'
);

-- 创建索引
CREATE INDEX idx_metrics_backtest_name_timestamp 
ON realtime_metrics (backtest_id, metric_name, timestamp DESC);
```

## 4. 性能优化配置

### 4.1 PostgreSQL 配置优化

```ini
# postgresql.conf 关键配置

# 内存配置
shared_buffers = 4GB                    # 系统内存的25%
effective_cache_size = 12GB              # 系统内存的75%
work_mem = 256MB                         # 单个查询工作内存
maintenance_work_mem = 1GB               # 维护操作内存

# 连接配置
max_connections = 200                    # 最大连接数
shared_preload_libraries = 'timescaledb' # 预加载TimescaleDB

# 查询优化
random_page_cost = 1.1                   # SSD优化
effective_io_concurrency = 200           # 并发IO

# WAL配置
wal_buffers = 64MB
checkpoint_completion_target = 0.9
max_wal_size = 4GB
min_wal_size = 1GB

# 并行查询
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_worker_processes = 8

# 日志配置
log_statement = 'mod'                    # 记录修改语句
log_min_duration_statement = 1000        # 记录慢查询(1秒)
log_checkpoints = on
log_connections = on
log_disconnections = on
```

### 4.2 TimescaleDB 特定优化

```sql
-- 设置数据保留策略
SELECT add_retention_policy('kline_data', INTERVAL '2 years');
SELECT add_retention_policy('trade_records', INTERVAL '1 year');
SELECT add_retention_policy('realtime_metrics', INTERVAL '3 months');

-- 启用数据压缩（节省存储空间）
ALTER TABLE kline_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol,timeframe',
    timescaledb.compress_orderby = 'timestamp DESC'
);

-- 设置压缩策略
SELECT add_compression_policy('kline_data', INTERVAL '7 days');

-- 创建连续聚合（预计算常用指标）
CREATE MATERIALIZED VIEW kline_daily_summary
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', timestamp) AS day,
    symbol,
    first(open, timestamp) AS day_open,
    max(high) AS day_high,
    min(low) AS day_low,
    last(close, timestamp) AS day_close,
    sum(volume) AS day_volume
FROM kline_data 
WHERE timeframe = '1h'
GROUP BY day, symbol;

-- 设置连续聚合刷新策略
SELECT add_continuous_aggregate_policy('kline_daily_summary',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);
```

## 5. 环境配置差异

### 5.1 开发环境配置

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: quant_trading_dev
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    command: >
      postgres
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c work_mem=64MB
      -c log_statement=all
      -c log_min_duration_statement=0

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data

volumes:
  postgres_dev_data:
  redis_dev_data:
```

### 5.2 生产环境配置

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: quant_trading_prod
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./postgresql.conf:/etc/postgresql/postgresql.conf
      - ./pg_hba.conf:/etc/postgresql/pg_hba.conf
    command: >
      postgres
      -c config_file=/etc/postgresql/postgresql.conf
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
        reservations:
          memory: 4G
          cpus: '2'

  pgbouncer:
    image: pgbouncer/pgbouncer:latest
    environment:
      DATABASES_HOST: postgres
      DATABASES_PORT: 5432
      DATABASES_USER: ${POSTGRES_USER}
      DATABASES_PASSWORD: ${POSTGRES_PASSWORD}
      DATABASES_DBNAME: quant_trading_prod
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 1000
      DEFAULT_POOL_SIZE: 25
    ports:
      - "6432:6432"
    depends_on:
      - postgres

volumes:
  postgres_prod_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/postgres
```

## 6. 数据库连接和基础操作

### 6.1 Python 连接示例

```python
# database.py
import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os

class DatabaseManager:
    def __init__(self):
        self.database_url = self._build_database_url()
        self.engine = create_async_engine(
            self.database_url,
            echo=False,  # 生产环境设为False
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.async_session = sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    
    def _build_database_url(self) -> str:
        """构建数据库连接URL"""
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', 'password')
        database = os.getenv('DB_NAME', 'quant_trading')
        
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话"""
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
        """执行原生SQL查询"""
        async with self.engine.begin() as conn:
            result = await conn.execute(query, params or {})
            return result.fetchall()

# 全局数据库管理器实例
db_manager = DatabaseManager()
```

### 6.2 数据操作示例

```python
# models.py
from sqlalchemy import Column, String, DECIMAL, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMPTZ
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class KlineData(Base):
    __tablename__ = 'kline_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    timestamp = Column(TIMESTAMPTZ, nullable=False)
    open = Column(DECIMAL(20, 8), nullable=False)
    high = Column(DECIMAL(20, 8), nullable=False)
    low = Column(DECIMAL(20, 8), nullable=False)
    close = Column(DECIMAL(20, 8), nullable=False)
    volume = Column(DECIMAL(20, 8), nullable=False)
    created_at = Column(TIMESTAMPTZ, default=func.now())

class BacktestResult(Base):
    __tablename__ = 'backtest_results'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_name = Column(String(100), nullable=False)
    parameters = Column(JSONB, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_balance = Column(DECIMAL(20, 8), nullable=False)
    final_balance = Column(DECIMAL(20, 8), nullable=False)
    total_return = Column(DECIMAL(10, 4), nullable=False)
    max_drawdown = Column(DECIMAL(10, 4), nullable=False)
    sharpe_ratio = Column(DECIMAL(10, 4))
    total_trades = Column(Integer, nullable=False)
    win_rate = Column(DECIMAL(5, 2), nullable=False)
    is_liquidated = Column(Boolean, default=False)
    created_at = Column(TIMESTAMPTZ, default=func.now())
    updated_at = Column(TIMESTAMPTZ, default=func.now(), onupdate=func.now())
```

### 6.3 数据访问层示例

```python
# data_access.py
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import select, and_, desc
from models import KlineData, BacktestResult
from database import db_manager

class KlineDataRepository:
    async def get_kline_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start_time: datetime, 
        end_time: datetime,
        limit: int = 10000
    ) -> List[KlineData]:
        """获取K线数据"""
        async with db_manager.get_session() as session:
            query = select(KlineData).where(
                and_(
                    KlineData.symbol == symbol,
                    KlineData.timeframe == timeframe,
                    KlineData.timestamp >= start_time,
                    KlineData.timestamp <= end_time
                )
            ).order_by(KlineData.timestamp).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def bulk_insert_kline_data(self, kline_data: List[Dict[str, Any]]) -> None:
        """批量插入K线数据"""
        async with db_manager.get_session() as session:
            session.add_all([
                KlineData(**data) for data in kline_data
            ])
            await session.commit()
    
    async def get_latest_timestamp(self, symbol: str, timeframe: str) -> Optional[datetime]:
        """获取最新数据时间戳"""
        async with db_manager.get_session() as session:
            query = select(KlineData.timestamp).where(
                and_(
                    KlineData.symbol == symbol,
                    KlineData.timeframe == timeframe
                )
            ).order_by(desc(KlineData.timestamp)).limit(1)
            
            result = await session.execute(query)
            timestamp = result.scalar_one_or_none()
            return timestamp

class BacktestRepository:
    async def save_backtest_result(self, result_data: Dict[str, Any]) -> str:
        """保存回测结果"""
        async with db_manager.get_session() as session:
            backtest = BacktestResult(**result_data)
            session.add(backtest)
            await session.flush()
            return str(backtest.id)
    
    async def get_backtest_results(
        self, 
        strategy_name: Optional[str] = None,
        limit: int = 100
    ) -> List[BacktestResult]:
        """获取回测结果列表"""
        async with db_manager.get_session() as session:
            query = select(BacktestResult)
            
            if strategy_name:
                query = query.where(BacktestResult.strategy_name == strategy_name)
            
            query = query.order_by(desc(BacktestResult.created_at)).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
```

## 7. 监控和维护

### 7.1 性能监控查询

```sql
-- 查看数据库大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 查看慢查询
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- 查看TimescaleDB chunk信息
SELECT 
    hypertable_name,
    chunk_name,
    range_start,
    range_end,
    pg_size_pretty(chunk_size) as size
FROM timescaledb_information.chunks 
ORDER BY range_start DESC;

-- 查看压缩状态
SELECT 
    hypertable_name,
    compression_status,
    uncompressed_heap_size,
    compressed_heap_size,
    compression_ratio
FROM timescaledb_information.compression_settings;
```

### 7.2 备份和恢复

```bash
# 创建备份脚本
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/postgres"
DB_NAME="quant_trading"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 全量备份
pg_dump -h localhost -U postgres -d $DB_NAME -f $BACKUP_DIR/full_backup_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/full_backup_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: full_backup_$DATE.sql.gz"
```

```bash
# 恢复脚本
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
DB_NAME="quant_trading"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# 解压备份文件
gunzip -c $BACKUP_FILE > /tmp/restore.sql

# 删除现有数据库
dropdb -h localhost -U postgres $DB_NAME

# 创建新数据库
createdb -h localhost -U postgres $DB_NAME

# 恢复数据
psql -h localhost -U postgres -d $DB_NAME -f /tmp/restore.sql

# 清理临时文件
rm /tmp/restore.sql

echo "Database restored from $BACKUP_FILE"
```

## 8. 故障排除

### 8.1 常见问题

**问题1: 连接数过多**

```sql
-- 查看当前连接数
SELECT count(*) FROM pg_stat_activity;

-- 查看连接详情
SELECT 
    datname,
    usename,
    application_name,
    client_addr,
    state,
    query_start
FROM pg_stat_activity 
WHERE state = 'active';

-- 终止空闲连接
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' AND query_start < now() - interval '1 hour';
```

**问题2: 查询性能慢**

```sql
-- 分析查询计划
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM kline_data 
WHERE symbol = 'ETH-USDC' 
AND timestamp BETWEEN '2023-01-01' AND '2023-12-31';

-- 更新表统计信息
ANALYZE kline_data;

-- 重建索引
REINDEX INDEX idx_kline_symbol_timeframe_timestamp;
```

**问题3: 磁盘空间不足**

```sql
-- 清理过期数据
SELECT drop_chunks('kline_data', INTERVAL '1 year');

-- 手动压缩数据
SELECT compress_chunk(chunk_name) 
FROM timescaledb_information.chunks 
WHERE hypertable_name = 'kline_data' 
AND range_end < now() - INTERVAL '1 week';

-- 清理WAL日志
SELECT pg_switch_wal();
CHECKPOINT;
```

## 9. 安全配置

### 9.1 用户权限管理

```sql
-- 创建应用用户
CREATE USER app_user WITH PASSWORD 'secure_password';

-- 创建只读用户
CREATE USER readonly_user WITH PASSWORD 'readonly_password';

-- 授权应用用户
GRANT CONNECT ON DATABASE quant_trading TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- 授权只读用户
GRANT CONNECT ON DATABASE quant_trading TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
```

### 9.2 网络安全配置

```ini
# pg_hba.conf 配置
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# 本地连接
local   all             postgres                                peer
local   all             all                                     md5

# IPv4 本地连接
host    all             all             127.0.0.1/32            md5

# 应用服务器连接
host    quant_trading   app_user        10.0.0.0/8              md5

# 禁止其他连接
host    all             all             0.0.0.0/0               reject
```

通过以上配置，您将拥有一个高

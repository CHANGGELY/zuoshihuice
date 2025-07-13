#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库配置和模型
"""

from sqlalchemy import create_engine, Column, String, Float, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import json
import uuid
from typing import Dict, Any, Optional
try:
    from core.config import settings
except ImportError:
    from fastapi_backend.core.config import settings

# 数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BacktestResult(Base):
    """回测结果模型"""
    __tablename__ = "backtest_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_name = Column(String, nullable=False, default="网格做市策略")
    symbol = Column(String, nullable=False)
    timeframe = Column(String, nullable=False, default="1m")
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    initial_capital = Column(Float, nullable=False)
    leverage = Column(Integer, nullable=False)
    spread_threshold = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=False)
    trade_count = Column(Integer, nullable=False)
    win_rate = Column(Float, nullable=False)
    final_equity = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    params_config = Column(Text, nullable=False)  # JSON字符串
    trade_history = Column(Text, nullable=False)  # JSON字符串
    equity_curve = Column(Text, nullable=False)   # JSON字符串
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "strategy_name": self.strategy_name,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "initial_capital": self.initial_capital,
            "leverage": self.leverage,
            "spread_threshold": self.spread_threshold,
            "total_return": self.total_return,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "trade_count": self.trade_count,
            "win_rate": self.win_rate,
            "final_equity": self.final_equity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "params_config": json.loads(self.params_config) if self.params_config else {},
            "trade_history": json.loads(self.trade_history) if self.trade_history else [],
            "equity_curve": json.loads(self.equity_curve) if self.equity_curve else []
        }
    
    @classmethod
    def from_backtest_result(cls, result: Dict[str, Any], params: Dict[str, Any]) -> "BacktestResult":
        """从回测结果创建数据库记录"""
        return cls(
            strategy_name="网格做市策略",
            symbol=params.get("symbol", "ETHUSDT"),
            start_date=params.get("startDate", ""),
            end_date=params.get("endDate", ""),
            initial_capital=params.get("initialCapital", 10000),
            leverage=params.get("leverage", 5),
            spread_threshold=params.get("spreadThreshold", 0.002),
            total_return=result.get("total_return", 0.0),
            max_drawdown=result.get("max_drawdown", 0.0),
            sharpe_ratio=result.get("sharpe_ratio", 0.0),
            trade_count=result.get("trade_count", 0),
            win_rate=result.get("win_rate", 0.0),
            final_equity=result.get("final_equity", 0.0),
            params_config=json.dumps(params),
            trade_history=json.dumps(result.get("trade_history", [])),
            equity_curve=json.dumps(result.get("equity_history", []))
        )

def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseService:
    """数据库服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_backtest_result(self, result: Dict[str, Any], params: Dict[str, Any]) -> str:
        """保存回测结果"""
        db_result = BacktestResult.from_backtest_result(result, params)
        self.db.add(db_result)
        self.db.commit()
        self.db.refresh(db_result)
        return db_result.id
    
    def get_backtest_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """获取回测结果"""
        result = self.db.query(BacktestResult).filter(BacktestResult.id == result_id).first()
        return result.to_dict() if result else None
    
    def get_backtest_history(self, limit: int = 50) -> list:
        """获取回测历史"""
        results = self.db.query(BacktestResult).order_by(BacktestResult.created_at.desc()).limit(limit).all()
        return [result.to_dict() for result in results]
    
    def delete_backtest_result(self, result_id: str) -> bool:
        """删除回测结果"""
        result = self.db.query(BacktestResult).filter(BacktestResult.id == result_id).first()
        if result:
            self.db.delete(result)
            self.db.commit()
            return True
        return False

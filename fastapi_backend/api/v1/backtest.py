#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测API路由
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import logging

try:
    from core.database import get_db, DatabaseService
    from services.backtest_service import backtest_service
except ImportError:
    from fastapi_backend.core.database import get_db, DatabaseService
    from fastapi_backend.services.backtest_service import backtest_service

logger = logging.getLogger(__name__)
router = APIRouter()

class BacktestParams(BaseModel):
    """回测参数模型"""
    symbol: str = Field(default="ETHUSDT", description="交易对")
    startDate: str = Field(..., description="开始日期 YYYY-MM-DD")
    endDate: str = Field(..., description="结束日期 YYYY-MM-DD")
    initialCapital: float = Field(default=10000, ge=100, description="初始资金")
    leverage: int = Field(default=5, ge=1, le=125, description="杠杆倍数")
    spreadThreshold: float = Field(default=0.002, ge=0.0001, le=0.1, description="价差阈值")
    positionRatio: float = Field(default=0.8, ge=0.1, le=1.0, description="仓位比例")
    orderRatio: float = Field(default=0.02, ge=0.001, le=0.1, description="下单比例")

class BacktestResponse(BaseModel):
    """回测响应模型"""
    success: bool
    message: str = ""
    result_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/run", response_model=BacktestResponse, summary="运行回测")
async def run_backtest(
    params: BacktestParams,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    运行回测策略
    
    - **symbol**: 交易对 (默认: ETHUSDT)
    - **startDate**: 开始日期
    - **endDate**: 结束日期  
    - **initialCapital**: 初始资金
    - **leverage**: 杠杆倍数
    - **spreadThreshold**: 价差阈值
    - **positionRatio**: 仓位比例
    - **orderRatio**: 下单比例
    """
    try:
        logger.info(f"🚀 收到回测请求: {params.dict()}")
        
        # 执行回测
        result = await backtest_service.run_backtest(params.dict())
        
        if not result.get("success", False):
            return BacktestResponse(
                success=False,
                error=result.get("error", "回测执行失败")
            )
        
        # 保存结果到数据库
        db_service = DatabaseService(db)
        result_id = db_service.save_backtest_result(
            result["result"], 
            params.dict()
        )
        
        logger.info(f"✅ 回测完成，结果ID: {result_id}")
        
        return BacktestResponse(
            success=True,
            message="回测完成",
            result_id=result_id,
            result=result["result"]
        )
        
    except Exception as e:
        logger.error(f"❌ 回测API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{result_id}", summary="获取回测结果")
async def get_backtest_result(
    result_id: str,
    db: Session = Depends(get_db)
):
    """获取指定ID的回测结果"""
    try:
        db_service = DatabaseService(db)
        result = db_service.get_backtest_result(result_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="回测结果不存在")
        
        return {
            "success": True,
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取回测结果错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", summary="获取回测历史")
async def get_backtest_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取回测历史记录"""
    try:
        db_service = DatabaseService(db)
        history = db_service.get_backtest_history(limit)
        
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"❌ 获取回测历史错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/results/{result_id}", summary="删除回测结果")
async def delete_backtest_result(
    result_id: str,
    db: Session = Depends(get_db)
):
    """删除指定的回测结果"""
    try:
        db_service = DatabaseService(db)
        success = db_service.delete_backtest_result(result_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="回测结果不存在")
        
        return {
            "success": True,
            "message": "回测结果已删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除回测结果错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/status", summary="获取缓存状态")
async def get_cache_status():
    """获取缓存系统状态"""
    try:
        status = await backtest_service.get_cache_status()
        return {
            "success": True,
            "cache_status": status
        }
    except Exception as e:
        logger.error(f"❌ 获取缓存状态错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/clear", summary="清空缓存")
async def clear_cache():
    """清空回测缓存"""
    try:
        await backtest_service.clear_cache()
        return {
            "success": True,
            "message": "缓存已清空"
        }
    except Exception as e:
        logger.error(f"❌ 清空缓存错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

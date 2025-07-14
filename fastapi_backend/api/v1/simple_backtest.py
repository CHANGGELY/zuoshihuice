#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化回测API - 完全避免线程锁序列化问题
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import subprocess
import json
import tempfile
import sys
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SimpleBacktestParams(BaseModel):
    """简化回测参数"""
    symbol: str = Field(default="ETHUSDT", description="交易对")
    startDate: str = Field(description="开始日期")
    endDate: str = Field(description="结束日期")
    initialCapital: float = Field(default=10000, ge=100, description="初始资金")
    leverage: int = Field(default=5, ge=1, le=125, description="杠杆倍数")
    spreadThreshold: float = Field(default=0.002, description="价差阈值")
    positionRatio: float = Field(default=0.8, description="仓位比例")
    orderRatio: float = Field(default=0.02, description="订单比例")

@router.post("/simple-run", summary="简化回测执行")
async def simple_run_backtest(params: SimpleBacktestParams):
    """简化的回测执行 - 完全避免序列化问题"""
    try:
        logger.info(f"🚀 开始简化回测: {params.dict()}")
        
        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent.parent
        
        # 创建临时参数文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(params.dict(), f, ensure_ascii=False, indent=2)
            params_file = f.name
        
        # 构建命令
        cmd = [
            sys.executable,
            str(project_root / "独立回测执行器.py"),
            "--params-file", params_file
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 执行子进程
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5分钟超时
            cwd=str(project_root)
        )
        
        # 清理临时文件
        Path(params_file).unlink(missing_ok=True)
        
        logger.info(f"子进程返回码: {result.returncode}")
        logger.info(f"子进程输出: {result.stdout[:500]}...")
        
        if result.returncode != 0:
            logger.error(f"子进程错误: {result.stderr}")
            return {
                "success": False,
                "error": f"回测执行失败: {result.stderr}",
                "error_type": "subprocess_error"
            }
        
        # 解析结果
        try:
            backtest_result = json.loads(result.stdout)
            
            if "error" in backtest_result:
                return {
                    "success": False,
                    "error": backtest_result["error"],
                    "error_type": backtest_result.get("error_type", "backtest_error")
                }
            
            return {
                "success": True,
                "result": backtest_result,
                "message": "回测完成"
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return {
                "success": False,
                "error": f"结果解析失败: {e}",
                "error_type": "json_error"
            }
        
    except subprocess.TimeoutExpired:
        logger.error("回测超时")
        return {
            "success": False,
            "error": "回测超时，请检查参数或减少回测时间范围",
            "error_type": "timeout"
        }
    except Exception as e:
        logger.error(f"简化回测失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "execution_error"
        }

@router.get("/test", summary="测试接口")
async def test_simple_api():
    """测试简化API是否正常工作"""
    return {
        "success": True,
        "message": "简化回测API正常工作",
        "timestamp": "2025-01-13"
    }

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步回测服务 - 完美解决Django/Flask崩溃问题
"""

import asyncio
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from decimal import Decimal

try:
    from core.config import settings
    from core.cache import cache_manager
except ImportError:
    from fastapi_backend.core.config import settings
    from fastapi_backend.core.cache import cache_manager

logger = logging.getLogger(__name__)

class AsyncBacktestService:
    """异步回测服务 - 高性能、稳定、可靠"""

    def __init__(self):
        self.project_root = settings.project_root
        self.backtest_engine = settings.backtest_engine

        # 添加项目根目录到Python路径
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
    
    async def run_backtest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """异步运行回测 - 直接异步执行，保持原始引擎完整性"""
        logger.info(f"🚀 开始异步回测: {params}")

        try:
            # 验证参数
            validated_params = self._validate_params(params)

            # 直接异步执行回测（不使用进程池）
            result = await asyncio.wait_for(
                self._execute_backtest_async(validated_params),
                timeout=settings.backtest_timeout
            )

            logger.info("✅ 回测完成")
            return self._format_result(result, validated_params)

        except asyncio.TimeoutError:
            logger.error("⏰ 回测超时")
            return {
                "success": False,
                "error": "回测超时，请检查参数或减少回测时间范围",
                "error_type": "timeout"
            }
        except Exception as e:
            logger.error(f"❌ 回测失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "execution_error"
            }
    
    def _validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证和标准化参数"""
        validated = {
            "symbol": params.get("symbol", "ETHUSDT"),
            "startDate": params.get("startDate", "2024-06-15"),
            "endDate": params.get("endDate", "2024-07-15"),
            "initialCapital": float(params.get("initialCapital", 10000)),
            "leverage": int(params.get("leverage", 5)),
            "spreadThreshold": float(params.get("spreadThreshold", 0.002)),
            "positionRatio": float(params.get("positionRatio", 0.8)),
            "orderRatio": float(params.get("orderRatio", 0.02))
        }
        
        # 参数范围验证
        if validated["leverage"] < 1 or validated["leverage"] > 125:
            raise ValueError("杠杆倍数必须在1-125之间")

        if validated["spreadThreshold"] < 0.0001 or validated["spreadThreshold"] > 0.1:
            raise ValueError("价差阈值必须在0.01%-10%之间")

        if validated["initialCapital"] < 100:
            raise ValueError("初始资金不能少于100")
        
        return validated

    async def _execute_backtest_async(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """异步执行回测 - 强制使用子进程完全隔离，避免线程锁问题"""
        try:
            # 🚀 强制使用子进程执行，完全避免线程锁序列化问题
            result = self._execute_backtest_subprocess(params)
            return result
        except Exception as e:
            logger.error(f"异步回测执行失败: {e}")
            return {"error": str(e)}

    def _execute_backtest_in_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """在独立进程中执行回测 - 强制使用子进程，完全避免线程锁问题"""
        try:
            # 🚀 强制使用子进程执行，避免线程锁序列化问题
            return self._execute_backtest_subprocess(params)
        except Exception as e:
            logger.error(f"子进程执行失败: {e}")
            raise
    
    def _execute_backtest_direct(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """直接导入原始回测引擎执行"""
        try:
            # 导入原始回测引擎
            from backtest_kline_trajectory import (
                run_backtest_with_params, 
                BACKTEST_CONFIG, 
                STRATEGY_CONFIG
            )
            
            # 更新回测配置
            BACKTEST_CONFIG.update({
                'start_date': params['startDate'],
                'end_date': params['endDate'],
                'initial_balance': params['initialCapital'],
                'plot_equity_curve': False,  # 禁用图表生成
            })
            
            # 更新策略配置
            STRATEGY_CONFIG.update({
                'leverage': params['leverage'],
                'bid_spread': params['spreadThreshold'],
                'ask_spread': params['spreadThreshold'],
                'max_position_value_ratio': params['positionRatio'],
                'position_size_ratio': params['orderRatio'],
            })
            
            # 运行回测
            result = run_backtest_with_params(
                strategy_params=None,  # 已经更新了全局配置
                market_params=None,
                use_cache=True  # 使用缓存提升性能
            )
            
            # 格式化结果
            return self._format_result(result, params)
            
        except Exception as e:
            logger.error(f"直接执行回测失败: {e}")
            raise
    
    def _execute_backtest_subprocess(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """使用子进程执行回测（备用方案）"""
        try:
            # 创建临时参数文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(params, f, ensure_ascii=False, indent=2)
                params_file = f.name
            
            # 构建命令
            cmd = [
                sys.executable,
                str(self.project_root / "独立回测执行器.py"),
                "--params-file", params_file
            ]
            
            # 执行子进程
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=settings.backtest_timeout,
                cwd=str(self.project_root)
            )
            
            # 清理临时文件
            Path(params_file).unlink(missing_ok=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"回测执行失败: {result.stderr}")
            
            # 解析结果
            return json.loads(result.stdout)
            
        except Exception as e:
            logger.error(f"子进程执行回测失败: {e}")
            raise
    
    def _format_result(self, result: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """格式化回测结果"""
        if not result or "error" in result:
            return {
                "success": False,
                "error": result.get("error", "回测执行失败"),
                "error_type": "backtest_error"
            }
        
        # 转换Decimal为float
        def convert_decimal(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_decimal(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimal(item) for item in obj]
            return obj
        
        formatted_result = convert_decimal(result)
        
        return {
            "success": True,
            "params": params,
            "result": formatted_result,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def get_cache_status(self) -> Dict[str, Any]:
        """获取缓存状态"""
        return cache_manager.get_status()
    
    async def clear_cache(self):
        """清空缓存"""
        cache_manager.clear_cache()
    
    def cleanup(self):
        """清理资源"""
        self.executor.shutdown(wait=True)
        logger.info("🧹 回测服务清理完成")

# 全局回测服务实例
backtest_service = AsyncBacktestService()

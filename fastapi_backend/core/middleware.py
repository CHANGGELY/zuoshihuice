#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中间件模块 - 性能监控、请求日志、错误处理
"""

import time
import logging
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from typing import Callable
import json

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        logger.info(f"📥 {request.method} {request.url.path} - 开始处理")
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 添加性能头
        response.headers["X-Process-Time"] = str(process_time)
        
        # 记录响应信息
        logger.info(
            f"📤 {request.method} {request.url.path} - "
            f"状态码: {response.status_code}, "
            f"处理时间: {process_time:.3f}s"
        )
        
        # 性能警告
        if process_time > 5.0:  # 超过5秒
            logger.warning(
                f"⚠️ 慢请求警告: {request.method} {request.url.path} "
                f"耗时 {process_time:.3f}s"
            )
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求详情
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        logger.info(
            f"🌐 请求详情: "
            f"IP={client_ip}, "
            f"Method={request.method}, "
            f"Path={request.url.path}, "
            f"UserAgent={user_agent[:50]}..."
        )
        
        response = await call_next(request)
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(
                f"❌ 未处理的异常: {request.method} {request.url.path} - {str(e)}",
                exc_info=True
            )
            
            # 返回统一的错误响应
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "服务器内部错误",
                    "message": "请稍后重试或联系管理员",
                    "path": str(request.url.path)
                }
            )

class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全模块 - 速率限制、认证、授权
"""

import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from typing import Dict, Deque
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """简单的内存速率限制器"""
    
    def __init__(self):
        # 存储每个IP的请求时间戳
        self.requests: Dict[str, Deque[float]] = defaultdict(lambda: deque())
        
        # 不同端点的限制配置
        self.limits = {
            "/api/v1/backtest/run": {"requests": 5, "window": 60},  # 回测：1分钟5次
            "/api/v1/backtest/cache/clear": {"requests": 2, "window": 300},  # 清缓存：5分钟2次
            "default": {"requests": 100, "window": 60}  # 默认：1分钟100次
        }
    
    def is_allowed(self, client_ip: str, endpoint: str) -> bool:
        """检查是否允许请求"""
        current_time = time.time()
        
        # 获取限制配置
        limit_config = self.limits.get(endpoint, self.limits["default"])
        max_requests = limit_config["requests"]
        window_seconds = limit_config["window"]
        
        # 获取该IP的请求历史
        ip_requests = self.requests[client_ip]
        
        # 清理过期的请求记录
        cutoff_time = current_time - window_seconds
        while ip_requests and ip_requests[0] < cutoff_time:
            ip_requests.popleft()
        
        # 检查是否超过限制
        if len(ip_requests) >= max_requests:
            logger.warning(
                f"🚫 速率限制触发: IP={client_ip}, "
                f"端点={endpoint}, "
                f"请求数={len(ip_requests)}/{max_requests}"
            )
            return False
        
        # 记录当前请求
        ip_requests.append(current_time)
        return True
    
    def get_remaining_requests(self, client_ip: str, endpoint: str) -> int:
        """获取剩余请求次数"""
        current_time = time.time()
        limit_config = self.limits.get(endpoint, self.limits["default"])
        max_requests = limit_config["requests"]
        window_seconds = limit_config["window"]
        
        ip_requests = self.requests[client_ip]
        cutoff_time = current_time - window_seconds
        
        # 清理过期记录
        while ip_requests and ip_requests[0] < cutoff_time:
            ip_requests.popleft()
        
        return max(0, max_requests - len(ip_requests))

# 全局速率限制器实例
rate_limiter = RateLimiter()

def check_rate_limit(request: Request):
    """速率限制检查依赖"""
    client_ip = request.client.host if request.client else "unknown"
    endpoint = request.url.path
    
    if not rate_limiter.is_allowed(client_ip, endpoint):
        remaining = rate_limiter.get_remaining_requests(client_ip, endpoint)
        raise HTTPException(
            status_code=429,
            detail={
                "error": "请求过于频繁",
                "message": "您的请求速度过快，请稍后再试",
                "remaining_requests": remaining,
                "endpoint": endpoint
            }
        )

class SecurityValidator:
    """安全验证器"""
    
    @staticmethod
    def validate_backtest_params(params: dict) -> bool:
        """验证回测参数的安全性"""
        try:
            # 检查杠杆范围
            leverage = params.get("leverage", 1)
            if not (1 <= leverage <= 100):
                logger.warning(f"⚠️ 异常杠杆参数: {leverage}")
                return False
            
            # 检查初始资金范围
            initial_capital = params.get("initialCapital", 0)
            if not (100 <= initial_capital <= 10000000):  # 100到1000万
                logger.warning(f"⚠️ 异常初始资金: {initial_capital}")
                return False
            
            # 检查价差阈值范围
            spread_threshold = params.get("spreadThreshold", 0)
            if not (0.0001 <= spread_threshold <= 0.1):  # 0.01%到10%
                logger.warning(f"⚠️ 异常价差阈值: {spread_threshold}")
                return False
            
            # 检查日期格式
            start_date = params.get("startDate", "")
            end_date = params.get("endDate", "")
            if not start_date or not end_date:
                logger.warning("⚠️ 缺少日期参数")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 参数验证失败: {e}")
            return False
    
    @staticmethod
    def sanitize_input(data: str) -> str:
        """输入数据清理"""
        if not isinstance(data, str):
            return str(data)
        
        # 移除潜在的危险字符
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        for char in dangerous_chars:
            data = data.replace(char, '')
        
        # 限制长度
        return data[:1000]  # 最大1000字符

# 全局安全验证器实例
security_validator = SecurityValidator()

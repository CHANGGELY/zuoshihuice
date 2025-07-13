#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证API路由 - 简化版本，专注于回测功能
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str

class LoginResponse(BaseModel):
    """登录响应模型"""
    success: bool
    message: str
    token: str = ""
    user: Dict[str, Any] = {}

@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(request: LoginRequest):
    """
    用户登录 - 简化版本
    
    目前支持演示账户：
    - 用户名: demo
    - 密码: demo123
    """
    try:
        # 简化的认证逻辑
        if request.username == "demo" and request.password == "demo123":
            return LoginResponse(
                success=True,
                message="登录成功",
                token="demo_token_12345",
                user={
                    "id": "demo_user",
                    "username": "demo",
                    "name": "演示用户",
                    "role": "user"
                }
            )
        else:
            return LoginResponse(
                success=False,
                message="用户名或密码错误"
            )
            
    except Exception as e:
        logger.error(f"❌ 登录错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout", summary="用户登出")
async def logout():
    """用户登出"""
    return {
        "success": True,
        "message": "登出成功"
    }

@router.get("/profile", summary="获取用户信息")
async def get_profile():
    """获取当前用户信息"""
    return {
        "success": True,
        "user": {
            "id": "demo_user",
            "username": "demo",
            "name": "演示用户",
            "role": "user"
        }
    }

@router.get("/permissions", summary="获取用户权限")
async def get_permissions():
    """获取用户权限列表"""
    return {
        "success": True,
        "permissions": [
            "backtest:run",
            "backtest:view",
            "market:view",
            "cache:manage"
        ]
    }

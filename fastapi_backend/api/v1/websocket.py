#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket API - 实时通信支持
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
from typing import List, Dict, Any
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.backtest_subscribers: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, connection_type: str = "general"):
        """连接WebSocket"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if connection_type == "backtest":
            self.backtest_subscribers.append(websocket)
        
        logger.info(f"✅ WebSocket连接建立: {connection_type}")
    
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if websocket in self.backtest_subscribers:
            self.backtest_subscribers.remove(websocket)
        
        logger.info("🔌 WebSocket连接断开")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"❌ 发送个人消息失败: {e}")
    
    async def broadcast(self, message: Dict[str, Any], connection_type: str = "general"):
        """广播消息"""
        connections = self.active_connections
        if connection_type == "backtest":
            connections = self.backtest_subscribers
        
        disconnected = []
        for connection in connections:
            try:
                await connection.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"❌ 广播消息失败: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_backtest_progress(self, progress: Dict[str, Any]):
        """广播回测进度"""
        message = {
            "type": "backtest_progress",
            "data": progress,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(message, "backtest")
    
    async def broadcast_backtest_result(self, result: Dict[str, Any]):
        """广播回测结果"""
        message = {
            "type": "backtest_result",
            "data": result,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(message, "backtest")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取连接统计"""
        return {
            "total_connections": len(self.active_connections),
            "backtest_subscribers": len(self.backtest_subscribers)
        }

# 全局连接管理器
manager = ConnectionManager()

@router.websocket("/general")
async def websocket_general(websocket: WebSocket):
    """通用WebSocket连接"""
    await manager.connect(websocket, "general")
    try:
        # 发送欢迎消息
        await manager.send_personal_message({
            "type": "welcome",
            "message": "WebSocket连接成功",
            "timestamp": asyncio.get_event_loop().time()
        }, websocket)
        
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                # 处理不同类型的消息
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    }, websocket)
                
                elif message.get("type") == "get_stats":
                    stats = manager.get_stats()
                    await manager.send_personal_message({
                        "type": "stats",
                        "data": stats,
                        "timestamp": asyncio.get_event_loop().time()
                    }, websocket)
                
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "无效的JSON格式",
                    "timestamp": asyncio.get_event_loop().time()
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.websocket("/backtest")
async def websocket_backtest(websocket: WebSocket):
    """回测专用WebSocket连接"""
    await manager.connect(websocket, "backtest")
    try:
        # 发送欢迎消息
        await manager.send_personal_message({
            "type": "backtest_connected",
            "message": "回测WebSocket连接成功",
            "timestamp": asyncio.get_event_loop().time()
        }, websocket)
        
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                # 处理回测相关消息
                if message.get("type") == "subscribe_progress":
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "message": "已订阅回测进度更新",
                        "timestamp": asyncio.get_event_loop().time()
                    }, websocket)
                
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "无效的JSON格式",
                    "timestamp": asyncio.get_event_loop().time()
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# 导出管理器供其他模块使用
__all__ = ["manager", "router"]

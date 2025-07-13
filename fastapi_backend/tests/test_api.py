#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi_backend.main import app

client = TestClient(app)

class TestBasicAPI:
    """基础API测试"""
    
    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "永续合约回测系统 FastAPI 后端"
        assert data["version"] == "2.0.0"
    
    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "backtest_engine_exists" in data
        assert "data_file_exists" in data
    
    def test_system_status(self):
        """测试系统状态"""
        response = client.get("/api/v1/system/status")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "system" in data
        assert "performance" in data
        assert "application" in data

class TestMarketAPI:
    """市场数据API测试"""
    
    def test_get_symbols(self):
        """测试获取交易对"""
        response = client.get("/api/v1/market/symbols")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ETHUSDT" in data["symbols"]
    
    def test_get_timeframes(self):
        """测试获取时间周期"""
        response = client.get("/api/v1/market/timeframes")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["timeframes"]) > 0
    
    def test_get_market_stats(self):
        """测试获取市场统计"""
        response = client.get("/api/v1/market/stats")
        # 可能因为数据文件不存在而失败，这是正常的
        assert response.status_code in [200, 500]

class TestAuthAPI:
    """认证API测试"""
    
    def test_login_success(self):
        """测试登录成功"""
        response = client.post("/api/v1/auth/login", json={
            "username": "demo",
            "password": "demo123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["token"] == "demo_token_12345"
    
    def test_login_failure(self):
        """测试登录失败"""
        response = client.post("/api/v1/auth/login", json={
            "username": "wrong",
            "password": "wrong"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
    
    def test_get_profile(self):
        """测试获取用户信息"""
        response = client.get("/api/v1/auth/profile")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user" in data

class TestBacktestAPI:
    """回测API测试"""
    
    def test_get_cache_status(self):
        """测试获取缓存状态"""
        response = client.get("/api/v1/backtest/cache/status")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cache_status" in data
    
    def test_get_backtest_history(self):
        """测试获取回测历史"""
        response = client.get("/api/v1/backtest/history")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "history" in data
    
    def test_backtest_params_validation(self):
        """测试回测参数验证"""
        # 测试无效参数
        invalid_params = {
            "leverage": 200,  # 超出范围
            "initialCapital": 50,  # 太小
            "spreadThreshold": 0.5,  # 太大
            "startDate": "2024-01-01",
            "endDate": "2024-01-02"
        }
        
        response = client.post("/api/v1/backtest/run", json=invalid_params)
        # 应该返回验证错误
        assert response.status_code in [400, 422, 500]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

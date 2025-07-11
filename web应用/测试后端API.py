#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端API功能
在没有前端的情况下测试所有API接口
"""

import requests
import json
from datetime import datetime

class APITester:
    """API测试器"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000/api/v1"
        self.token = None
        self.session = requests.Session()
    
    def test_health(self):
        """测试健康检查"""
        print("🔍 测试健康检查API...")
        try:
            response = self.session.get(f"{self.base_url}/health/")
            if response.status_code == 200:
                print("✅ 健康检查通过")
                print(f"响应: {response.json()}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    def test_register(self, username="testuser", email="test@example.com", password="testpass123"):
        """测试用户注册"""
        print(f"🔍 测试用户注册API...")
        try:
            data = {
                "username": username,
                "email": email,
                "password": password,
                "confirm_password": password
            }
            response = self.session.post(f"{self.base_url}/auth/register/", json=data)
            
            if response.status_code == 200:
                result = response.json()
                self.token = result['data']['token']
                self.session.headers.update({'Authorization': f'Token {self.token}'})
                print("✅ 用户注册成功")
                print(f"用户: {result['data']['user']['username']}")
                print(f"Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ 用户注册失败: {response.status_code}")
                print(f"错误: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 用户注册异常: {e}")
            return False
    
    def test_login(self, username="testuser", password="testpass123"):
        """测试用户登录"""
        print(f"🔍 测试用户登录API...")
        try:
            data = {
                "username": username,
                "password": password
            }
            response = self.session.post(f"{self.base_url}/auth/login/", json=data)
            
            if response.status_code == 200:
                result = response.json()
                self.token = result['data']['token']
                self.session.headers.update({'Authorization': f'Token {self.token}'})
                print("✅ 用户登录成功")
                print(f"用户: {result['data']['user']['username']}")
                return True
            else:
                print(f"❌ 用户登录失败: {response.status_code}")
                print(f"错误: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 用户登录异常: {e}")
            return False
    
    def test_market_data(self):
        """测试市场数据API"""
        print("🔍 测试市场数据API...")
        try:
            # 测试K线数据
            params = {
                'symbol': 'ETHUSDT',
                'timeframe': '1m',
                'start_date': '2024-06-15',
                'end_date': '2024-06-16',
                'limit': 10
            }
            response = self.session.get(f"{self.base_url}/market/klines/", params=params)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ K线数据获取成功")
                print(f"数据条数: {len(result['data'])}")
                if result['data']:
                    print(f"示例数据: {result['data'][0]}")
                return True
            else:
                print(f"❌ K线数据获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 市场数据异常: {e}")
            return False
    
    def test_market_stats(self):
        """测试市场统计API"""
        print("🔍 测试市场统计API...")
        try:
            params = {'symbol': 'ETHUSDT'}
            response = self.session.get(f"{self.base_url}/market/stats/", params=params)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 市场统计获取成功")
                print(f"当前价格: {result['data']['last_price']}")
                print(f"24h涨跌: {result['data']['price_24h_change']}%")
                print(f"24h成交量: {result['data']['volume_24h']}")
                return True
            else:
                print(f"❌ 市场统计获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 市场统计异常: {e}")
            return False
    
    def test_backtest(self):
        """测试回测API"""
        print("🔍 测试回测API...")
        try:
            # 回测配置
            config = {
                "symbol": "ETHUSDT",
                "timeframe": "1m",
                "start_date": "2024-06-15",
                "end_date": "2024-06-16",
                "initial_balance": 10000,
                "leverage": 10,
                "spread": 0.002,
                "position_ratio": 0.8,
                "order_ratio": 0.02,
                "stop_loss_ratio": 0.05,
                "take_profit_ratio": 0.03
            }
            
            response = self.session.post(f"{self.base_url}/backtest/run/", json=config)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 回测启动成功")
                print(f"回测ID: {result['data']['backtest_id']}")
                print(f"状态: {result['data']['status']}")
                return True
            else:
                print(f"❌ 回测启动失败: {response.status_code}")
                print(f"错误: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 回测异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🧪 后端API功能测试")
        print("=" * 60)
        
        # 1. 健康检查
        if not self.test_health():
            print("❌ 后端服务不可用，请先启动Django服务器")
            return False
        
        print()
        
        # 2. 用户注册（如果失败则尝试登录）
        if not self.test_register():
            print("注册失败，尝试登录现有用户...")
            if not self.test_login():
                print("❌ 无法获取认证token")
                return False
        
        print()
        
        # 3. 市场数据测试
        self.test_market_data()
        print()
        
        # 4. 市场统计测试
        self.test_market_stats()
        print()
        
        # 5. 回测测试
        self.test_backtest()
        
        print("\n" + "=" * 60)
        print("🎉 API测试完成！")
        print("=" * 60)
        print("💡 提示：")
        print("1. 安装Node.js后可以使用完整的前端界面")
        print("2. 访问 http://127.0.0.1:8000/admin/ 进行后台管理")
        print("3. 所有API接口都可以通过HTTP客户端调用")
        print("=" * 60)
        
        return True

def main():
    """主函数"""
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

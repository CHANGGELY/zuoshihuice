#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前后端连接
验证前端能否成功调用后端API完成回测
"""

import requests
import json
import time

def test_backend_health():
    """测试后端健康状态"""
    try:
        print("🔍 测试后端健康状态...")
        response = requests.get('http://localhost:8000/api/v1/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 后端健康状态: {data}")
            return True
        else:
            print(f"❌ 后端健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_backtest_api():
    """测试回测API"""
    try:
        print("🚀 测试回测API...")
        
        # 准备回测参数（与前端发送的格式一致）
        params = {
            'strategy': 'grid_making',
            'initial_capital': 10000,
            'leverage': 5,
            'start_date': '2024-06-15',
            'end_date': '2024-07-15',
            'bid_spread': 0.002,
            'ask_spread': 0.002
        }
        
        print(f"📋 发送参数: {params}")
        
        # 发送请求
        response = requests.post(
            'http://localhost:8000/api/v1/backtest/run/',
            json=params,
            headers={'Content-Type': 'application/json'},
            timeout=300
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                data = result.get('data', {})
                print("✅ 回测成功!")
                print(f"📈 总收益率: {data.get('total_return', 0) * 100:.2f}%")
                print(f"🔢 交易次数: {data.get('total_trades', 0)}")
                print(f"💰 最终资金: {data.get('final_balance', 0):.2f}")
                print(f"📊 最大回撤: {data.get('max_drawdown', 0) * 100:.2f}%")
                print(f"📝 交易记录数量: {len(data.get('trades', []))}")
                return True
            else:
                print(f"❌ 回测失败: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"❌ 响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 回测API测试失败: {e}")
        return False

def test_frontend_connection():
    """测试前端连接"""
    try:
        print("🌐 测试前端连接...")
        response = requests.get('http://localhost:5174', timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务正常运行")
            return True
        else:
            print(f"❌ 前端连接失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始前后端连接测试...")
    print("=" * 50)
    
    # 测试后端健康状态
    backend_ok = test_backend_health()
    print()
    
    # 测试前端连接
    frontend_ok = test_frontend_connection()
    print()
    
    # 测试回测API
    if backend_ok:
        api_ok = test_backtest_api()
    else:
        api_ok = False
        print("⏭️ 跳过回测API测试（后端不可用）")
    
    print()
    print("=" * 50)
    print("🏁 测试结果总结:")
    print(f"🔧 后端服务: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"🌐 前端服务: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    print(f"🚀 回测API: {'✅ 正常' if api_ok else '❌ 异常'}")
    
    if backend_ok and api_ok:
        print("\n🎉 恭喜！前后端连接测试全部通过！")
        print("💡 现在可以在前端界面进行回测了")
        return True
    else:
        print("\n⚠️ 存在问题，需要进一步排查")
        return False

if __name__ == '__main__':
    main()

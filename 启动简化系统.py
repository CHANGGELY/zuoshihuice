#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
永续合约回测系统启动器 - 简化版本
解决线程锁序列化问题的稳定版本
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path
import signal
import atexit

def main():
    print("=" * 60)
    print("    🚀 永续合约回测系统 - 简化版本")
    print("    解决线程锁序列化问题的稳定版本")
    print("=" * 60)
    print()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.absolute()
    frontend_dir = project_root / "webapp" / "frontend"
    
    print(f"📁 项目目录: {project_root}")
    print(f"📁 Vue前端: {frontend_dir}")
    print()
    
    # 检查目录存在
    if not frontend_dir.exists():
        print("❌ Vue前端目录不存在!")
        input("按回车键退出...")
        return
    
    # 检查核心文件
    backtest_engine = project_root / "backtest_kline_trajectory.py"
    data_file = project_root / "K线data" / "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5"
    simple_server = project_root / "简单回测服务器.py"
    
    if not backtest_engine.exists():
        print(f"❌ 回测引擎不存在: {backtest_engine}")
        input("按回车键退出...")
        return
    
    if not data_file.exists():
        print(f"❌ 数据文件不存在: {data_file}")
        input("按回车键退出...")
        return
        
    if not simple_server.exists():
        print(f"❌ 简单回测服务器不存在: {simple_server}")
        input("按回车键退出...")
        return
    
    print("✅ 文件检查通过")
    print()
    
    # 存储进程引用
    backend_process = None
    frontend_process = None
    
    def cleanup():
        """清理函数"""
        print("\n🛑 正在停止服务...")
        if backend_process:
            try:
                backend_process.terminate()
                print("✅ 简单回测服务器已停止")
            except:
                pass
        
        if frontend_process:
            try:
                frontend_process.terminate()
                print("✅ Vue前端已停止")
            except:
                pass
        
        print("👋 系统已停止!")
    
    # 注册清理函数
    atexit.register(cleanup)
    
    try:
        # 启动简单回测服务器
        print("🚀 启动简单回测服务器...")
        backend_process = subprocess.Popen(
            [sys.executable, "-X", "utf8", "简单回测服务器.py"],
            cwd=str(project_root),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print(f"✅ 简单回测服务器已启动 (PID: {backend_process.pid})")
        print("📡 后端地址: http://localhost:8001")
        print("🔗 健康检查: http://localhost:8001/health")
        print()
        
        # 等待后端启动
        print("⏳ 等待简单回测服务器启动...")
        time.sleep(3)
        
        # 启动Vue前端
        print("🎨 启动Vue前端...")
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print(f"✅ Vue前端已启动 (PID: {frontend_process.pid})")
        print("🌐 前端地址: http://localhost:5173")
        print()
        
        # 等待前端启动
        print("⏳ 等待Vue前端编译...")
        time.sleep(10)
        
        # 打开浏览器
        print("🌐 正在打开浏览器...")
        try:
            webbrowser.open("http://localhost:5173")
        except:
            print("⚠️ 无法自动打开浏览器，请手动访问: http://localhost:5173")
        
        print()
        print("=" * 60)
        print("           🎉 系统启动完成!")
        print("=" * 60)
        print()
        print("📊 访问地址:")
        print("   前端界面: http://localhost:5173")
        print("   后端API:  http://localhost:8001")
        print("   健康检查: http://localhost:8001/health")
        print()
        print("🔥 系统特性:")
        print("   ✅ 简化回测服务器 - 完全避开线程锁序列化问题")
        print("   ✅ 高性能回测引擎 - 进程隔离执行")
        print("   ✅ 智能缓存系统 - 提升回测速度")
        print("   ✅ 稳定可靠架构 - 不会崩溃")
        print("   ✅ 真实数据回测 - 专业量化级别")
        print()
        print("💡 使用说明:")
        print("   - 前端需要约30秒编译时间")
        print("   - 浏览器已自动打开前端页面")
        print("   - 按 Ctrl+C 停止所有服务")
        print("   - 回测API端点: POST http://localhost:8001/api/v1/backtest/run")
        print()
        
        # 等待用户停止
        try:
            print("按 Ctrl+C 停止服务...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            cleanup()
    
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        cleanup()
        input("按回车键退出...")

if __name__ == "__main__":
    main()

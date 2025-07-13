#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI + Vue 永续合约回测系统启动器
火力全开版本！
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
    print("    🚀 FastAPI + Vue 永续合约回测系统")
    print("    火力全开版本 - 高性能异步后端")
    print("=" * 60)
    print()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.absolute()
    fastapi_dir = project_root / "fastapi_backend"
    frontend_dir = project_root / "web应用" / "frontend"
    
    print(f"📁 项目目录: {project_root}")
    print(f"📁 FastAPI后端: {fastapi_dir}")
    print(f"📁 Vue前端: {frontend_dir}")
    print()
    
    # 检查目录存在
    if not fastapi_dir.exists():
        print("❌ FastAPI后端目录不存在!")
        input("按回车键退出...")
        return
    
    if not frontend_dir.exists():
        print("❌ Vue前端目录不存在!")
        input("按回车键退出...")
        return
    
    # 检查核心文件
    backtest_engine = project_root / "backtest_kline_trajectory.py"
    data_file = project_root / "K线data" / "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5"
    
    if not backtest_engine.exists():
        print(f"❌ 回测引擎不存在: {backtest_engine}")
        input("按回车键退出...")
        return
    
    if not data_file.exists():
        print(f"❌ 数据文件不存在: {data_file}")
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
                print("✅ FastAPI后端已停止")
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
        # 启动FastAPI后端
        print("🚀 启动FastAPI后端...")
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=str(fastapi_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print(f"✅ FastAPI后端已启动 (PID: {backend_process.pid})")
        print("📡 后端地址: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs")
        print()
        
        # 等待后端启动
        print("⏳ 等待FastAPI后端启动...")
        time.sleep(5)
        
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
        print("   后端API:  http://localhost:8000")
        print("   API文档:  http://localhost:8000/docs")
        print()
        print("🔥 新功能特性:")
        print("   ✅ FastAPI异步后端 - 解决崩溃问题")
        print("   ✅ 高性能回测引擎 - 进程隔离")
        print("   ✅ 智能缓存系统 - 提升回测速度")
        print("   ✅ WebSocket实时通信 - 回测进度推送")
        print("   ✅ 自动API文档 - 开发调试利器")
        print()
        print("💡 使用说明:")
        print("   - 前端需要约30秒编译时间")
        print("   - 浏览器已自动打开前端页面")
        print("   - 按 Ctrl+C 停止所有服务")
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
永续合约回测系统 - 终极启动器
绝对有效的一键启动解决方案
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def main():
    print("=" * 50)
    print("    永续合约做市策略回测系统")
    print("=" * 50)
    print()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.absolute()
    frontend_dir = project_root / "web应用" / "frontend"
    backend_file = project_root / "最终稳定后端.py"
    
    print(f"项目目录: {project_root}")
    print(f"后端文件: {backend_file}")
    print(f"前端目录: {frontend_dir}")
    print()
    
    # 检查文件存在
    if not backend_file.exists():
        print("❌ 后端文件不存在!")
        input("按回车键退出...")
        return
    
    if not frontend_dir.exists():
        print("❌ 前端目录不存在!")
        input("按回车键退出...")
        return
    
    print("✅ 文件检查通过")
    print()
    
    try:
        # 启动后端
        print("🚀 启动后端服务...")
        backend_process = subprocess.Popen(
            [sys.executable, str(backend_file)],
            cwd=str(project_root),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print(f"✅ 后端已启动 (PID: {backend_process.pid})")
        print("📡 后端地址: http://localhost:5000")
        print()
        
        # 等待后端启动
        print("⏳ 等待后端启动...")
        time.sleep(3)
        
        # 启动前端
        print("🎨 启动前端服务...")
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print(f"✅ 前端已启动 (PID: {frontend_process.pid})")
        print("🌐 前端地址: http://localhost:5173")
        print()
        
        # 等待前端启动
        print("⏳ 等待前端编译...")
        time.sleep(8)
        
        # 打开浏览器
        print("🌐 正在打开浏览器...")
        try:
            webbrowser.open("http://localhost:5173")
        except:
            print("⚠️ 无法自动打开浏览器，请手动访问: http://localhost:5173")
        
        print()
        print("=" * 50)
        print("           🎉 启动完成!")
        print("=" * 50)
        print()
        print("📊 访问地址:")
        print("   前端: http://localhost:5173")
        print("   后端: http://localhost:5000")
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
            print("\n🛑 正在停止服务...")
            
            # 停止进程
            try:
                frontend_process.terminate()
                print("✅ 前端服务已停止")
            except:
                pass
            
            try:
                backend_process.terminate()
                print("✅ 后端服务已停止")
            except:
                pass
            
            print("👋 服务已停止!")
    
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()

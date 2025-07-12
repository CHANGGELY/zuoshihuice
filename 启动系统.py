#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
永续合约做市策略回测系统启动器
一键启动前后端服务
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python: {result.stdout.strip()}")
        else:
            print("❌ Python 未安装或未添加到PATH")
            return False
    except FileNotFoundError:
        print("❌ Python 未安装或未添加到PATH")
        return False
    
    # 检查Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
        else:
            print("❌ Node.js 未安装或未添加到PATH")
            return False
    except FileNotFoundError:
        print("❌ Node.js 未安装或未添加到PATH")
        return False
    
    return True

def start_backend():
    """启动后端服务"""
    print("\n🚀 启动后端服务...")
    
    backend_script = Path(__file__).parent / "最终稳定后端.py"
    if not backend_script.exists():
        print("❌ 后端脚本不存在")
        return None
    
    try:
        # 启动后端进程
        process = subprocess.Popen(
            [sys.executable, "-X", "utf8", str(backend_script)],
            cwd=Path(__file__).parent,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print("✅ 后端服务已启动 (PID: {})".format(process.pid))
        print("📡 后端地址: http://localhost:5000")
        return process
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("\n🎨 启动前端服务...")
    
    frontend_dir = Path(__file__).parent / "web应用" / "frontend"
    if not frontend_dir.exists():
        print("❌ 前端目录不存在")
        return None
    
    vite_script = frontend_dir / "node_modules" / "vite" / "bin" / "vite.js"
    if not vite_script.exists():
        print("❌ Vite未安装，请在前端目录运行: npm install")
        return None
    
    try:
        # 启动前端进程
        process = subprocess.Popen(
            ["node", str(vite_script), "--host", "0.0.0.0", "--port", "5173"],
            cwd=frontend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print("✅ 前端服务已启动 (PID: {})".format(process.pid))
        print("🌐 前端地址: http://localhost:5173")
        return process
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("    🚀 永续合约做市策略回测系统启动器")
    print("=" * 60)
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请安装必要的软件")
        input("按回车键退出...")
        return
    
    # 启动后端
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ 后端启动失败")
        input("按回车键退出...")
        return
    
    # 等待后端启动
    print("\n⏳ 等待后端服务启动...")
    time.sleep(3)
    
    # 启动前端
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ 前端启动失败")
        backend_process.terminate()
        input("按回车键退出...")
        return
    
    # 等待前端启动
    print("\n⏳ 等待前端服务启动...")
    time.sleep(5)
    
    # 显示启动完成信息
    print("\n" + "=" * 60)
    print("           🎉 系统启动完成！")
    print("=" * 60)
    print("\n📊 系统地址:")
    print("   前端界面: http://localhost:5173")
    print("   后端API:  http://localhost:5000")
    print("\n💡 使用说明:")
    print("   1. 等待前端编译完成（约30秒）")
    print("   2. 浏览器会自动打开前端界面")
    print("   3. 在策略回测页面设置参数并运行回测")
    print("   4. 在结果分析页面查看详细图表")
    print("\n🛑 停止服务:")
    print("   按 Ctrl+C 或关闭此窗口")
    
    # 自动打开浏览器
    try:
        print("\n🌐 正在打开浏览器...")
        webbrowser.open("http://localhost:5173")
    except Exception as e:
        print(f"⚠️  无法自动打开浏览器: {e}")
        print("请手动访问: http://localhost:5173")
    
    # 等待用户停止
    try:
        print("\n按 Ctrl+C 停止所有服务...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        
        # 停止进程
        if frontend_process:
            frontend_process.terminate()
            print("✅ 前端服务已停止")
        
        if backend_process:
            backend_process.terminate()
            print("✅ 后端服务已停止")
        
        print("👋 再见！")

if __name__ == "__main__":
    main()

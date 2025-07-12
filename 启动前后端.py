#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 一键启动前后端
永续合约做市策略回测平台 - 超简单启动脚本
"""

import subprocess
import time
import sys
from pathlib import Path

def main():
    """一键启动前后端"""
    print("🚀 启动永续合约做市策略回测平台...")

    # 项目路径
    project_root = Path(__file__).parent
    backend_script = project_root / "最终稳定后端.py"
    frontend_dir = project_root / "web应用" / "frontend"

    # 启动后端
    print("📡 启动后端服务...")
    backend_process = subprocess.Popen([
        sys.executable, "-X", "utf8", str(backend_script)
    ], cwd=project_root)

    # 等待后端启动
    time.sleep(3)

    # 启动前端
    print("🌐 启动前端服务...")
    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ], cwd=frontend_dir)

    # 等待前端启动
    time.sleep(5)

    print("\n" + "=" * 50)
    print("🎉 启动完成！")
    print("🔧 后端: http://localhost:8000")
    print("📊 前端: http://localhost:5174")
    print("🚀 回测: http://localhost:5174/backtest")
    print("=" * 50)
    print("按 Ctrl+C 停止服务")

    try:
        # 保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ 已停止")

if __name__ == "__main__":
    main()

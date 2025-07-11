#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端启动脚本
解决npm run dev的问题
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def start_vite_server():
    """启动Vite开发服务器"""
    print("🚀 启动前端开发服务器...")

    # 获取当前目录
    frontend_dir = Path(__file__).parent

    # 检查node_modules是否存在
    node_modules = frontend_dir / 'node_modules'
    if not node_modules.exists():
        print("❌ node_modules不存在，请先运行 npm install")
        return False

    # 检查vite是否存在
    vite_js = node_modules / 'vite' / 'bin' / 'vite.js'
    if not vite_js.exists():
        print("❌ Vite未安装")
        return False

    try:
        # 启动Vite服务器
        print("⏳ 正在启动Vite...")

        # 设置环境变量
        env = os.environ.copy()
        env['NODE_ENV'] = 'development'

        # 使用node直接运行vite.js
        cmd = [
            'node',
            str(vite_js),
            '--host', '0.0.0.0',
            '--port', '5173'
        ]

        print(f"执行命令: {' '.join(cmd)}")

        # 启动进程
        process = subprocess.Popen(
            cmd,
            cwd=frontend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1,
            universal_newlines=True
        )

        print("✅ Vite服务器已启动")
        print("📊 前端地址: http://localhost:5173")
        print("🔧 后端地址: http://localhost:8000")
        print("=" * 50)
        print("按 Ctrl+C 停止服务")
        print("=" * 50)

        # 实时输出日志
        try:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
        except KeyboardInterrupt:
            print("\n🛑 正在停止服务...")
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ 服务已停止")
            except subprocess.TimeoutExpired:
                process.kill()
                print("🔪 强制停止服务")

        return True

    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🌐 前端开发服务器启动器")
    print("=" * 50)
    
    success = start_vite_server()
    
    if not success:
        print("❌ 前端启动失败")
        sys.exit(1)

if __name__ == "__main__":
    main()

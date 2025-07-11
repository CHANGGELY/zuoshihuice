#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Web应用启动脚本
自动启动Django后端和Vue前端开发服务器
"""

import os
import sys
import subprocess
import time
import threading
import signal
from pathlib import Path

class WebAppLauncher:
    """Web应用启动器"""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        
        # 项目路径
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / 'backend'
        self.frontend_dir = self.project_root / 'frontend'
        
    def check_dependencies(self):
        """检查依赖"""
        print("🔍 检查依赖...")
        
        # 检查Python依赖
        requirements_file = self.backend_dir / 'requirements.txt'
        if requirements_file.exists():
            print("✅ 找到Python依赖文件")
        else:
            print("❌ 未找到requirements.txt")
            return False
            
        # 检查Node.js依赖
        package_json = self.frontend_dir / 'package.json'
        if package_json.exists():
            print("✅ 找到Node.js依赖文件")
        else:
            print("❌ 未找到package.json")
            return False
            
        return True
    
    def install_backend_deps(self):
        """安装后端依赖"""
        print("📦 检查Python依赖...")
        try:
            # 检查关键依赖是否已安装
            import django
            import rest_framework
            import pandas
            print("✅ 主要Python依赖已安装")
            return True
        except ImportError:
            print("📦 安装Python依赖...")
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
                ], cwd=self.backend_dir, check=True, capture_output=True, text=True)
                print("✅ Python依赖安装完成")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Python依赖安装失败: {e}")
                # 尝试安装基础依赖
                try:
                    basic_deps = ['django', 'djangorestframework', 'django-cors-headers', 'pandas', 'python-dotenv', 'dj-database-url']
                    subprocess.run([
                        sys.executable, '-m', 'pip', 'install'
                    ] + basic_deps, check=True, capture_output=True, text=True)
                    print("✅ 基础依赖安装完成")
                    return True
                except subprocess.CalledProcessError:
                    print("❌ 无法安装依赖，请手动安装")
                    return False
    
    def install_frontend_deps(self):
        """安装前端依赖"""
        print("📦 检查Node.js依赖...")
        try:
            # 检查是否有node_modules
            node_modules = self.frontend_dir / 'node_modules'
            if not node_modules.exists():
                print("📦 安装Node.js依赖...")
                result = subprocess.run(['npm', 'install'], cwd=self.frontend_dir,
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print("✅ Node.js依赖安装完成")
                else:
                    print(f"❌ npm install失败: {result.stderr}")
                    return False
            else:
                print("✅ Node.js依赖已存在")
            return True
        except subprocess.TimeoutExpired:
            print("❌ npm install超时，请手动安装")
            return False
        except subprocess.CalledProcessError as e:
            print(f"❌ Node.js依赖安装失败: {e}")
            return False
        except FileNotFoundError:
            print("❌ 未找到npm命令，请先安装Node.js")
            print("💡 请访问 https://nodejs.org/ 下载安装Node.js")
            return False
    
    def setup_backend(self):
        """设置后端"""
        print("⚙️ 设置Django后端...")
        try:
            # 创建.env文件
            env_file = self.backend_dir / '.env'
            if not env_file.exists():
                example_env = self.backend_dir / '.env.example'
                if example_env.exists():
                    import shutil
                    shutil.copy(example_env, env_file)
                    print("✅ 创建.env文件")
                else:
                    # 创建基础.env文件
                    env_content = """# Django设置
SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True

# 数据库设置 (开发环境使用SQLite)
# DATABASE_URL=

# CORS设置
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# 数据文件路径
DATA_ROOT=../K线data
"""
                    with open(env_file, 'w', encoding='utf-8') as f:
                        f.write(env_content)
                    print("✅ 创建默认.env文件")

            # 运行数据库迁移
            print("🔄 运行数据库迁移...")
            result = subprocess.run([
                sys.executable, 'manage.py', 'migrate'
            ], cwd=self.backend_dir, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ 数据库迁移完成")
            else:
                print(f"❌ 数据库迁移失败: {result.stderr}")
                return False

            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 后端设置失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 后端设置异常: {e}")
            return False
    
    def start_backend(self):
        """启动后端服务"""
        print("🚀 启动Django后端服务...")
        try:
            # 使用UTF-8编码启动Django
            self.backend_process = subprocess.Popen([
                sys.executable, '-X', 'utf8', 'manage.py', 'runserver', '127.0.0.1:8000'
            ], cwd=self.backend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
               text=True, encoding='utf-8')

            # 等待后端启动
            print("⏳ 等待Django服务启动...")
            time.sleep(5)

            if self.backend_process.poll() is None:
                print("✅ Django后端服务启动成功 (http://localhost:8000)")
                return True
            else:
                # 获取错误信息
                stdout, stderr = self.backend_process.communicate()
                print("❌ Django后端服务启动失败")
                if stderr:
                    print(f"错误信息: {stderr}")
                return False

        except Exception as e:
            print(f"❌ 启动后端服务失败: {e}")
            return False
    
    def start_frontend(self):
        """启动前端服务"""
        print("🚀 启动Vue前端服务...")
        try:
            # 检查package.json是否存在
            package_json = self.frontend_dir / 'package.json'
            if not package_json.exists():
                print("❌ 未找到package.json文件")
                return False

            self.frontend_process = subprocess.Popen([
                'npm', 'run', 'dev'
            ], cwd=self.frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
               text=True, encoding='utf-8')

            # 等待前端启动
            print("⏳ 等待Vue服务启动...")
            time.sleep(8)

            if self.frontend_process.poll() is None:
                print("✅ Vue前端服务启动成功 (http://localhost:5173)")
                return True
            else:
                # 获取错误信息
                stdout, stderr = self.frontend_process.communicate()
                print("❌ Vue前端服务启动失败")
                if stderr:
                    print(f"错误信息: {stderr}")
                return False

        except FileNotFoundError:
            print("❌ 未找到npm命令，请确保Node.js已正确安装")
            return False
        except Exception as e:
            print(f"❌ 启动前端服务失败: {e}")
            return False
    
    def monitor_processes(self):
        """监控进程状态"""
        while self.running:
            time.sleep(5)
            
            # 检查后端进程
            if self.backend_process and self.backend_process.poll() is not None:
                print("⚠️ Django后端服务已停止")
                break
                
            # 检查前端进程
            if self.frontend_process and self.frontend_process.poll() is not None:
                print("⚠️ Vue前端服务已停止")
                break
    
    def stop_services(self):
        """停止服务"""
        print("\n🛑 正在停止服务...")
        self.running = False
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
                print("✅ Django后端服务已停止")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print("🔪 强制停止Django后端服务")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
                print("✅ Vue前端服务已停止")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                print("🔪 强制停止Vue前端服务")
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n🛑 接收到信号 {signum}，正在停止服务...")
        self.stop_services()
        sys.exit(0)
    
    def run(self):
        """运行Web应用"""
        print("=" * 60)
        print("🌐 永续合约做市策略回测平台 - Web应用启动器")
        print("=" * 60)
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # 1. 检查依赖
            if not self.check_dependencies():
                print("💡 提示：请确保项目文件完整")
                return False

            # 2. 安装依赖
            print("\n📦 安装依赖阶段...")
            if not self.install_backend_deps():
                print("💡 提示：可以尝试手动运行: pip install django djangorestframework")
                return False

            # 前端依赖是可选的，如果失败也继续
            frontend_ok = self.install_frontend_deps()
            if not frontend_ok:
                print("⚠️ 前端依赖安装失败，将只启动后端服务")

            # 3. 设置后端
            print("\n⚙️ 后端设置阶段...")
            if not self.setup_backend():
                print("💡 提示：请检查Django配置和数据库设置")
                return False

            # 4. 启动服务
            print("\n🚀 启动服务阶段...")
            if not self.start_backend():
                print("💡 提示：请检查端口8000是否被占用")
                return False

            # 只有前端依赖安装成功才启动前端
            if frontend_ok:
                if not self.start_frontend():
                    print("⚠️ 前端启动失败，但后端服务正常运行")
            else:
                print("⚠️ 跳过前端启动，只运行后端服务")
            
            print("\n" + "=" * 60)
            print("🎉 Web应用启动成功！")
            print("📊 前端地址: http://localhost:5173")
            print("🔧 后端地址: http://localhost:8000")
            print("📚 API文档: http://localhost:8000/admin")
            print("=" * 60)
            print("按 Ctrl+C 停止服务")
            
            # 5. 监控进程
            monitor_thread = threading.Thread(target=self.monitor_processes)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # 等待用户中断
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False
        finally:
            self.stop_services()
        
        return True

def main():
    """主函数"""
    launcher = WebAppLauncher()
    success = launcher.run()
    
    if success:
        print("👋 感谢使用永续合约做市策略回测平台！")
    else:
        print("❌ 启动失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()

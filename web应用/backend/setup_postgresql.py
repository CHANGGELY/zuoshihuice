#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL数据库设置脚本
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path

class PostgreSQLSetup:
    """PostgreSQL设置类"""
    
    def __init__(self):
        self.db_name = 'trading_platform'
        self.db_user = 'trading_user'
        self.db_password = 'trading_password_2024'
        self.db_host = 'localhost'
        self.db_port = '5432'
        
    def check_postgresql_installed(self):
        """检查PostgreSQL是否已安装"""
        try:
            result = subprocess.run(['psql', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ PostgreSQL已安装: {result.stdout.strip()}")
                return True
            else:
                print("❌ PostgreSQL未安装")
                return False
        except FileNotFoundError:
            print("❌ PostgreSQL未安装或未添加到PATH")
            return False
    
    def install_postgresql_windows(self):
        """在Windows上安装PostgreSQL的说明"""
        print("📋 Windows PostgreSQL安装说明:")
        print("1. 下载PostgreSQL安装程序:")
        print("   https://www.postgresql.org/download/windows/")
        print("2. 运行安装程序，设置超级用户密码")
        print("3. 确保PostgreSQL服务已启动")
        print("4. 将PostgreSQL的bin目录添加到PATH环境变量")
        print("   通常位于: C:\\Program Files\\PostgreSQL\\15\\bin")
        print("\n安装完成后，请重新运行此脚本")
        
    def create_database_and_user(self):
        """创建数据库和用户"""
        try:
            print("🔧 连接到PostgreSQL...")
            
            # 连接到默认数据库
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database='postgres',
                user='postgres',
                password=input("请输入PostgreSQL超级用户密码: ")
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # 检查用户是否存在
            cursor.execute(
                "SELECT 1 FROM pg_roles WHERE rolname = %s",
                (self.db_user,)
            )
            
            if not cursor.fetchone():
                print(f"👤 创建用户: {self.db_user}")
                cursor.execute(
                    f"CREATE USER {self.db_user} WITH PASSWORD %s",
                    (self.db_password,)
                )
            else:
                print(f"✅ 用户已存在: {self.db_user}")
            
            # 检查数据库是否存在
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.db_name,)
            )
            
            if not cursor.fetchone():
                print(f"🗄️ 创建数据库: {self.db_name}")
                cursor.execute(f"CREATE DATABASE {self.db_name}")
                cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {self.db_name} TO {self.db_user}")
            else:
                print(f"✅ 数据库已存在: {self.db_name}")
            
            cursor.close()
            conn.close()
            
            print("✅ 数据库和用户创建完成")
            return True
            
        except psycopg2.Error as e:
            print(f"❌ PostgreSQL操作失败: {e}")
            return False
        except KeyboardInterrupt:
            print("\n❌ 操作被用户取消")
            return False
    
    def create_env_file(self):
        """创建.env文件"""
        try:
            env_file = Path('.env')
            
            database_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
            
            env_content = f"""# Django设置
SECRET_KEY=django-insecure-postgresql-setup-key-change-in-production
DEBUG=True

# PostgreSQL数据库设置
DATABASE_URL={database_url}

# CORS设置
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# 数据文件路径
DATA_ROOT=../K线data

# 回测设置
DEFAULT_LEVERAGE=125
DEFAULT_SPREAD=0.002
DEFAULT_POSITION_RATIO=0.8
DEFAULT_ORDER_RATIO=0.02
"""
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            print(f"✅ 创建.env文件: {env_file.absolute()}")
            return True
            
        except Exception as e:
            print(f"❌ 创建.env文件失败: {e}")
            return False
    
    def run_migrations(self):
        """运行数据库迁移"""
        try:
            print("🔄 运行数据库迁移...")
            
            # 运行迁移
            result = subprocess.run([
                sys.executable, 'manage.py', 'migrate'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 数据库迁移完成")
                print(result.stdout)
                return True
            else:
                print("❌ 数据库迁移失败")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ 运行迁移失败: {e}")
            return False
    
    def create_superuser(self):
        """创建Django超级用户"""
        try:
            print("👑 创建Django超级用户...")
            
            # 交互式创建超级用户
            result = subprocess.run([
                sys.executable, 'manage.py', 'createsuperuser'
            ])
            
            if result.returncode == 0:
                print("✅ 超级用户创建完成")
                return True
            else:
                print("❌ 超级用户创建失败")
                return False
                
        except Exception as e:
            print(f"❌ 创建超级用户失败: {e}")
            return False
    
    def test_connection(self):
        """测试数据库连接"""
        try:
            print("🔍 测试数据库连接...")
            
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            print(f"✅ 数据库连接成功")
            print(f"PostgreSQL版本: {version[0]}")
            return True
            
        except psycopg2.Error as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def setup(self):
        """完整设置流程"""
        print("=" * 60)
        print("🐘 PostgreSQL数据库设置")
        print("=" * 60)
        
        # 1. 检查PostgreSQL是否已安装
        if not self.check_postgresql_installed():
            self.install_postgresql_windows()
            return False
        
        # 2. 创建数据库和用户
        if not self.create_database_and_user():
            return False
        
        # 3. 创建.env文件
        if not self.create_env_file():
            return False
        
        # 4. 测试连接
        if not self.test_connection():
            return False
        
        # 5. 运行迁移
        if not self.run_migrations():
            return False
        
        # 6. 创建超级用户
        create_superuser = input("\n是否创建Django超级用户? (y/n): ").lower().strip()
        if create_superuser == 'y':
            self.create_superuser()
        
        print("\n" + "=" * 60)
        print("🎉 PostgreSQL设置完成！")
        print("=" * 60)
        print(f"数据库名称: {self.db_name}")
        print(f"用户名: {self.db_user}")
        print(f"主机: {self.db_host}:{self.db_port}")
        print("=" * 60)
        
        return True

def main():
    """主函数"""
    setup = PostgreSQLSetup()
    success = setup.setup()
    
    if not success:
        print("\n❌ PostgreSQL设置失败")
        sys.exit(1)

if __name__ == "__main__":
    main()

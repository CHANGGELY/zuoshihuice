@echo off
chcp 65001 >nul
title 永续合约K线回测系统 - 完整Web版

echo.
echo ========================================
echo    🚀 永续合约K线回测系统
echo    完整Web版本 v4.0
echo ========================================
echo.

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请安装Python 3.8+并添加到系统PATH
    pause
    exit /b 1
)

:: 检查数据文件
if not exist "K线data\ETHUSDT_1m_2019-11-01_to_2025-06-15.h5" (
    echo ❌ K线数据文件不存在
    echo 请确保文件存在: K线data\ETHUSDT_1m_2019-11-01_to_2025-06-15.h5
    pause
    exit /b 1
)

:: 检查回测引擎
if not exist "backtest_kline_trajectory.py" (
    echo ❌ 回测引擎不存在
    echo 请确保文件存在: backtest_kline_trajectory.py
    pause
    exit /b 1
)

:: 检查进度回测执行器
if not exist "进度回测执行器.py" (
    echo ❌ 进度回测执行器不存在
    echo 请确保文件存在: 进度回测执行器.py
    pause
    exit /b 1
)

:: 检查统一回测服务器
if not exist "统一回测服务器.py" (
    echo ❌ 统一回测服务器不存在
    echo 请确保文件存在: 统一回测服务器.py
    pause
    exit /b 1
)

:: 检查前端服务器
if not exist "前端服务器.py" (
    echo ❌ 前端服务器不存在
    echo 请确保文件存在: 前端服务器.py
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

:: 启动后端服务器 (端口8001)
echo 🔧 启动后端服务器 (端口8001)...
start "后端服务器" cmd /k "python -X utf8 统一回测服务器.py"

:: 等待后端服务器启动
timeout /t 3 /nobreak >nul

:: 启动前端服务器 (端口3000)
echo 🌐 启动前端服务器 (端口3000)...
start "前端服务器" cmd /k "python -X utf8 前端服务器.py"

:: 等待前端服务器启动
timeout /t 3 /nobreak >nul

:: 打开浏览器
echo 🚀 打开Web界面...
start "" "http://localhost:3000"

echo.
echo ========================================
echo    🎉 完整Web系统启动成功！
echo ========================================
echo.
echo 🌐 前端地址: http://localhost:3000
echo 🔧 后端地址: http://localhost:8001
echo.
echo 💡 系统架构:
echo   前端服务器 (端口3000) ← 用户界面
echo   后端服务器 (端口8001) ← 数据和回测
echo.
echo 🎯 功能特色:
echo   ✅ 专业Web前端界面
echo   ✅ K线图表 + 交易标记
echo   ✅ 实时资金曲线图
echo   ✅ 完整回测指标
echo   ✅ 进度监控
echo   ✅ 服务器状态监控
echo.
echo 📋 使用说明:
echo 1. 浏览器会自动打开 http://localhost:3000
echo 2. 首先点击"📊 加载K线数据"
echo 3. 设置回测参数后点击"🚀 开始回测"
echo 4. 查看K线图上的交易标记和资金曲线
echo.
echo 🛑 关闭系统: 关闭所有命令行窗口
echo.
pause

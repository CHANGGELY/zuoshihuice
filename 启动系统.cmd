@echo off
chcp 65001 >nul
title 永续合约做市策略回测系统启动器

echo.
echo ========================================
echo    永续合约做市策略回测系统启动器
echo ========================================
echo.

echo [1/3] 检查环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未安装或未添加到PATH
    echo 请安装Python并添加到系统PATH
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js 未安装或未添加到PATH
    echo 请安装Node.js并添加到系统PATH
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

echo [2/3] 启动后端服务...
echo 正在启动Flask后端服务器...
start "回测系统后端" cmd /c "python -X utf8 最终稳定后端.py"

echo.
echo [3/3] 启动前端服务...
echo 等待3秒让后端启动...
timeout /t 3 /nobreak >nul

echo 正在启动Vue前端服务器...
cd /d "%~dp0web应用\frontend"
start "回测系统前端" cmd /c "node node_modules\vite\bin\vite.js --host 0.0.0.0 --port 5173"

echo.
echo ========================================
echo           启动完成！
echo ========================================
echo.
echo 📊 系统地址:
echo   前端界面: http://localhost:5173
echo   后端API:  http://localhost:5000
echo.
echo 💡 使用说明:
echo   1. 等待前端编译完成（约30秒）
echo   2. 打开浏览器访问前端界面
echo   3. 在策略回测页面设置参数并运行回测
echo   4. 在结果分析页面查看详细图表
echo.
echo 🛑 停止服务:
echo   关闭弹出的两个命令行窗口即可
echo.
echo 按任意键关闭此窗口...
pause >nul

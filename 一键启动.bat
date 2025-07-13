@echo off
chcp 65001 >nul
title 永续合约回测系统 - 一键启动

echo.
echo ==========================================
echo     永续合约做市策略回测系统
echo ==========================================
echo.

echo [1/2] 启动后端服务...
cd /d "%~dp0"
start "后端服务" cmd /k "python 最终稳定后端.py"

echo.
echo [2/2] 启动前端服务...
timeout /t 3 /nobreak >nul
cd /d "%~dp0web应用\frontend"
start "前端服务" cmd /k "npm run dev"

echo.
echo ==========================================
echo           启动完成！
echo ==========================================
echo.
echo 📊 访问地址:
echo    前端: http://localhost:5173
echo    后端: http://localhost:5000
echo.
echo 💡 说明:
echo    - 等待30秒让前端编译完成
echo    - 浏览器会自动打开前端页面
echo    - 关闭弹出的窗口即可停止服务
echo.

timeout /t 5 /nobreak >nul
start http://localhost:5173

echo 按任意键关闭此窗口...
pause >nul

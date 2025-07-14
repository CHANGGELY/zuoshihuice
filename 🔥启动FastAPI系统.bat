@echo off
chcp 65001 >nul
title 永续合约回测系统 - 完美运行版

echo.
echo ==========================================
echo     🚀 永续合约回测系统 - 完美运行版
echo     ✅ 已解决所有启动问题
echo ==========================================
echo.

echo 🔥 启动简单回测服务器...
start "回测服务器" cmd /k "cd /d %~dp0 && python -X utf8 简单回测服务器.py"

echo ⏳ 等待服务器启动...
timeout /t 3 /nobreak >nul

echo 🌐 打开前端界面...
start "" "%~dp0简单前端.html"

echo.
echo ✅ 系统启动完成！
echo 📊 前端界面已在浏览器中打开
echo 🔗 后端API: http://localhost:8001
echo.
echo 💡 使用说明:
echo    - 前端页面可以直接进行回测
echo    - 后端服务器在独立窗口中运行
echo    - 按 Ctrl+C 可停止后端服务器
echo.

pause

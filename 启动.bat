@echo off
chcp 65001 >nul
echo 🚀 启动永续合约做市策略回测平台...
echo.

echo 📡 启动后端服务...
start "后端服务" python -X utf8 最终稳定后端.py

timeout /t 3 /nobreak >nul

echo 🌐 启动前端服务...
cd web应用\frontend
start "前端服务" npm run dev

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo 🎉 启动完成！
echo 🔧 后端: http://localhost:8000
echo 📊 前端: http://localhost:5174  
echo 🚀 回测: http://localhost:5174/backtest
echo ========================================
echo.
echo 💡 提示: 关闭此窗口将停止所有服务
pause

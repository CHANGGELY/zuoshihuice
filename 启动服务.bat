@echo off
chcp 65001 >nul
echo 🚀 启动永续合约做市策略回测系统
echo.

echo 📋 检查环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未安装或未添加到PATH
    pause
    exit /b 1
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js 未安装或未添加到PATH
    pause
    exit /b 1
)

echo ✅ 环境检查通过

echo.
echo 🔧 启动后端服务...
start "后端服务" cmd /k "python -X utf8 最终稳定后端.py"

echo.
echo ⏳ 等待后端服务启动...
timeout /t 3 /nobreak >nul

echo.
echo 🎨 启动前端服务...
cd web应用\frontend
start "前端服务" cmd /k "node node_modules\vite\bin\vite.js --host 0.0.0.0 --port 5173"

echo.
echo ✅ 服务启动完成！
echo.
echo 📖 使用说明：
echo   - 后端服务: http://127.0.0.1:5000
echo   - 前端界面: http://127.0.0.1:5173
echo   - 请等待前端编译完成后访问前端界面
echo.
echo 🔧 如需停止服务，请关闭对应的命令行窗口
echo.
pause

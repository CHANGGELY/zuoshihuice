@echo off
chcp 65001 >nul
title Web Trading Backtest System

echo.
echo ========================================
echo    Web Trading Backtest System
echo    Starting Frontend and Backend...
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

:: Check data file
if not exist "K线data\ETHUSDT_1m_2019-11-01_to_2025-06-15.h5" (
    echo ERROR: Data file not found
    echo Please ensure file exists: K线data\ETHUSDT_1m_2019-11-01_to_2025-06-15.h5
    pause
    exit /b 1
)

:: Check backend server
if not exist "后端回测服务器.py" (
    echo ERROR: Backend server not found
    echo Please ensure file exists: 后端回测服务器.py
    pause
    exit /b 1
)

:: Check frontend server
if not exist "前端服务器.py" (
    echo ERROR: Frontend server not found
    echo Please ensure file exists: 前端服务器.py
    pause
    exit /b 1
)

echo Environment check passed
echo.

:: Start backend server (port 8001)
echo Starting backend server (port 8001)...
start "Backend Server" cmd /k "python -X utf8 后端回测服务器.py"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend server (port 3000)
echo Starting frontend server (port 3000)...
start "Frontend Server" cmd /k "python -X utf8 前端服务器.py"

:: Wait for frontend to start
timeout /t 3 /nobreak >nul

:: Open browser
echo Opening web interface...
start "" "http://localhost:3000"

echo.
echo ========================================
echo    System Started Successfully!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8001
echo.
echo To stop: Close all command windows
echo.
pause

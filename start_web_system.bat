@echo off
chcp 65001 >nul
setlocal ENABLEDELAYEDEXPANSION

title Web Trading Backtest System (FastAPI 8000)

echo.
echo ========================================
echo    Web Trading Backtest System
echo    FastAPI backend + static frontend on 8000
echo ========================================
echo.

:: Proxy (use local HTTP proxy)
set HTTP_PROXY=http://127.0.0.1:10808
set HTTPS_PROXY=%HTTP_PROXY%
set NO_PROXY=localhost,127.0.0.1

:: Python check
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python 3.11+ and add to PATH
    pause
    exit /b 1
)

:: Data dir check
if not exist "K线data" (
    echo Creating data directory: K线data
    mkdir "K线data"
)

:: Cache dir check
if not exist "cache" (
    echo Creating cache directory: cache
    mkdir "cache"
)

:: Activate venv if exists
if exist ".venv\Scripts\activate.bat" (
  call .venv\Scripts\activate.bat
)

:: Start FastAPI backend (serves static index on /)
echo Starting FastAPI backend server (port 8000)...
start "FastAPI Backend" cmd /k "python -m uvicorn fastapi_backend.main:app --host 0.0.0.0 --port 8000 --reload"

:: Give server a moment
timeout /t 3 /nobreak >nul

:: Open browser to backend root (static frontend)
start "" "http://localhost:8000"

echo.
echo ========================================
echo    System Started Successfully!
echo ========================================
echo.
echo UI:  http://localhost:8000

echo Press any key to exit launcher...
pause >nul
endlocal

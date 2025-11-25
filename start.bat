@echo off
REM Tesoro Boricua - Windows Start Script

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║    🇵🇷 Tesoro Boricua - Launching Application              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH!
    echo    Please install Python 3.7+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH!
    echo    Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo ✓ Python and Node.js found!
echo.
echo 🚀 Starting Backend Server...
start cmd /k python backend_server.py

REM Wait for backend to start
timeout /t 2 /nobreak

echo.
echo 🚀 Starting React Frontend...
cd react_ui
call npm start

pause

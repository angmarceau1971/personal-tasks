@echo off
setlocal enabledelayedexpansion
cls
echo.
echo ==========================================
echo    🔄 Restarting Task Dashboard Server
echo ==========================================
echo.

echo 🔍 Checking for processes using port 8081...

REM Find processes using port 8081 and extract PIDs
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8081 ^| findstr LISTENING') do (
    set PID=%%a
    if defined PID (
        echo 🛑 Found process using port 8081 with PID: !PID!
        echo 💀 Terminating process !PID!...
        taskkill /PID !PID! /F >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✅ Successfully terminated process !PID!
        ) else (
            echo ⚠️  Could not terminate process !PID! ^(may have already stopped^)
        )
    )
)

REM Give a moment for processes to fully terminate
echo ⏱️  Waiting 2 seconds for cleanup...
timeout /t 2 /nobreak >nul

echo.
echo 🚀 Starting Task Dashboard server...
echo.

REM Start the Python server
python server.py

echo.
echo 🛑 Server stopped.
echo.
pause 
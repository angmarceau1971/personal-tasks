@echo off
cls
echo.
echo ==========================================
echo    🔄 Kill Port 8081 and Restart Server
echo ==========================================
echo.

echo 🔍 Finding processes using port 8081...

REM More robust approach - get all PIDs using port 8081
for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":8081 "') do (
    echo 🛑 Killing process with PID: %%i
    taskkill /PID %%i /F >nul 2>&1
)

echo ⏱️  Waiting 2 seconds for cleanup...
timeout /t 2 /nobreak >nul

echo.
echo 🚀 Starting Task Dashboard server...
echo   📱 Local: http://localhost:8081
echo   🌐 Network: http://192.168.1.190:8081
echo.

python server.py

echo.
echo 🛑 Server stopped.
pause 
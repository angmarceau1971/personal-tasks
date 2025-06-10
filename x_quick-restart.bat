@echo off
cls
echo.
echo ==========================================
echo    🔄 Quick Server Restart
echo ==========================================
echo.

echo 🛑 Stopping any Python processes...
taskkill /IM python.exe /F >nul 2>&1
taskkill /IM pythonw.exe /F >nul 2>&1

echo ⏱️  Waiting for cleanup...
timeout /t 3 /nobreak >nul

echo 🚀 Starting Task Dashboard server...
echo.
python server.py

pause 
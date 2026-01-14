@echo off
echo ========================================
echo  Starting Student Classification System
echo ========================================
echo.

:: Start Backend in background
echo [1/2] Starting Backend API (port 5000)...
start "Backend API" cmd /c "cd /d %~dp0..\backend && python app.py"

:: Wait for backend to start
timeout /t 3 /nobreak > nul

:: Start Frontend
echo [2/2] Starting Frontend (port 8080)...
echo.
echo ========================================
echo  Frontend: http://localhost:8080
echo  Backend:  http://localhost:5000
echo ========================================
echo.
cd /d %~dp0
python -m http.server 8080

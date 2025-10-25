@echo off
REM Demo Bank Startup Script - Port 8001 (FIXED)
echo ========================================
echo Starting Demo Bank on Port 8001
echo ========================================

REM Kill any existing process on port 8001
echo Checking for existing processes on port 8001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    echo Killing process %%a
    taskkill /F /PID %%a 2>nul
)

REM Start backend on port 8001
echo Starting Demo Bank Backend...
cd backend
start cmd /k "..\venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8001"

REM Wait a bit for backend to start
timeout /t 5 /nobreak

REM Start frontend
echo Starting Demo Bank Frontend...
cd ..\frontend
start cmd /k "npm run dev"

echo.
echo ========================================
echo Demo Bank Started Successfully!
echo Backend:  http://localhost:8001
echo Frontend: http://localhost:3000
echo ========================================

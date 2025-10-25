@echo off
REM EchoBank Startup Script - Port 8000 (FIXED)
echo ========================================
echo Starting EchoBank on Port 8000
echo ========================================

REM Kill any existing process on port 8000
echo Checking for existing processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Killing process %%a
    taskkill /F /PID %%a 2>nul
)

REM Start backend on port 8000
echo Starting EchoBank Backend...
cd backend
start cmd /k "..\venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 5 /nobreak

REM Start frontend
echo Starting EchoBank Frontend...
cd ..\frontend
start cmd /k "npm run dev"

echo.
echo ========================================
echo EchoBank Started Successfully!
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo ========================================

@echo off
echo ========================================
echo Stopping all Python processes...
echo ========================================
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Starting FastAPI Backend (Port 8000)...
echo ========================================
cd /d "%~dp0food_api"
start "FastAPI Backend" cmd /k "python -m uvicorn app.main:app --reload"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Starting Flask AI Agent (Port 5000)...
echo ========================================
cd /d "%~dp0food_chatbot_agent"
start "Flask AI Agent" cmd /k "python agent.py"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Starting React Frontend (Port 5173/5174)...
echo ========================================
cd /d "%~dp0chatbot_frontend"
start "React Frontend" cmd /k "npm run dev"

cd /d "%~dp0"
echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo FastAPI Backend: http://localhost:8000
echo Flask AI Agent: http://localhost:5000
echo React Frontend: http://localhost:5174
echo.
echo Press any key to exit this window...
pause >nul

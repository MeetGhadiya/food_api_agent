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
start "FastAPI Backend" cmd /k "cd /d "%~dp0food_api" && venv\Scripts\activate && uvicorn app.main:app --reload"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Starting Flask AI Agent (Port 5000)...
echo ========================================
start "Flask AI Agent" cmd /k "cd /d "%~dp0food_chatbot_agent" && venv\Scripts\activate && python agent.py"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Starting React Frontend (Port 5173/5174)...
echo ========================================
start "React Frontend" cmd /k "cd /d "%~dp0chatbot_frontend" && npm run dev"

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

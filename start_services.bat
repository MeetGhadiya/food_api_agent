@echo off
echo ============================================
echo Starting Food Delivery Services
echo ============================================

REM Kill any existing Python processes
taskkill /F /IM python.exe 2>nul

timeout /t 2 /nobreak >nul

REM Start FastAPI
echo.
echo [1/3] Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "cd food_api && python -m uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

REM Start AI Agent
echo [2/3] Starting AI Agent...
start "AI Agent" cmd /k "cd food_chatbot_agent && python agent.py"

timeout /t 3 /nobreak >nul

REM Start React Frontend
echo [3/3] Starting React Frontend...
start "React Frontend" cmd /k "cd chatbot_frontend && npm run dev"

echo.
echo ============================================
echo All services started!
echo ============================================
echo.
echo FastAPI: http://localhost:8000
echo AI Agent: http://localhost:5000
echo React: http://localhost:5173
echo.
echo Press any key to stop all services...
pause >nul

REM Cleanup
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul

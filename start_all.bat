@echo off
echo ===================================
echo   AI Food Delivery Chatbot
echo   Starting All Services...
echo ===================================
echo.

REM Check if .env exists
if not exist "food_chatbot_agent\.env" (
    echo [ERROR] Missing .env file!
    echo.
    echo Please create food_chatbot_agent\.env with:
    echo GOOGLE_API_KEY=your_key_here
    echo FASTAPI_BASE_URL=http://localhost:8000
    echo.
    echo Get API key from: https://makersuite.google.com/app/apikey
    echo.
    pause
    exit /b 1
)

echo [1/3] Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "cd food_api && C:/Users/Skill/Desktop/m/python.exe -m uvicorn app.main:app --reload"
timeout /t 3 /nobreak >nul

echo [2/3] Starting AI Agent...
start "AI Agent" cmd /k "cd food_chatbot_agent && C:/Users/Skill/Desktop/m/python.exe agent.py"
timeout /t 3 /nobreak >nul

echo [3/3] Starting React Frontend...
start "React Frontend" cmd /k "cd chatbot_frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ===================================
echo   All Services Started!
echo ===================================
echo.
echo FastAPI Backend:  http://localhost:8000
echo AI Agent:         http://localhost:5000
echo React Frontend:   http://localhost:5173
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul
start http://localhost:5173
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping services...
taskkill /FI "WINDOWTITLE eq FastAPI Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq AI Agent*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq React Frontend*" /T /F >nul 2>&1
echo.
echo All services stopped.
pause

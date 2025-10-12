@echo off
echo ============================================
echo   Starting Food Delivery Chatbot System
echo ============================================
echo.

echo [1/3] Starting FastAPI Backend (Port 8000)...
start "FastAPI Backend" cmd /k "cd /d "%~dp0food_api" && start_api.bat"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Flask AI Agent (Port 5000)...
start "Flask AI Agent" cmd /k "cd /d "%~dp0food_chatbot_agent" && start_agent.bat"
timeout /t 3 /nobreak >nul

echo [3/3] Starting React Frontend (Port 5173)...
start "React Frontend" cmd /k "cd /d "%~dp0chatbot_frontend" && start_frontend.bat"
timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo   All Services Starting!
echo ============================================
echo.
echo FastAPI Backend:  http://localhost:8000
echo Flask AI Agent:   http://localhost:5000
echo React Frontend:   http://localhost:5173
echo.
echo Opening frontend in 5 seconds...
timeout /t 5 /nobreak >nul
start http://localhost:5173
echo.
echo Press any key to exit (services will keep running)
pause >nul

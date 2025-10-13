@echo off
cls
echo ===============================================================================
echo                    FOODIEEXPRESS V2.0 - ALL SERVICES LAUNCHER
echo ===============================================================================
echo.
echo Starting all services for FoodieExpress...
echo.
echo Services:
echo   [1] FastAPI Backend (Port 8000) - Restaurant API with Reviews
echo   [2] Flask AI Agent (Port 5000) - Gemini AI Chatbot
echo   [3] React Frontend (Port 5173) - User Interface
echo.
echo ===============================================================================
echo.

REM Check if MongoDB is required
echo [INFO] Make sure MongoDB Atlas is accessible
echo        Connection string configured in food_api/app/database.py
echo.

REM Start FastAPI Backend
echo [1/3] Starting FastAPI Backend...
cd /d "%~dp0food_api"
start "FoodieExpress - FastAPI Backend" cmd /k "python -m uvicorn app.main:app --reload"
timeout /t 3 >nul

REM Start Flask AI Agent
echo [2/3] Starting Flask AI Chatbot Agent...
cd /d "%~dp0food_chatbot_agent"
start "FoodieExpress - AI Agent" cmd /k "python agent.py"
timeout /t 3 >nul

REM Start React Frontend
echo [3/3] Starting React Frontend...
cd /d "%~dp0chatbot_frontend"
start "FoodieExpress - React Frontend" cmd /k "npm run dev"
timeout /t 5 >nul

echo.
echo ===============================================================================
echo                            ALL SERVICES STARTED!
echo ===============================================================================
echo.
echo Services are running in separate terminal windows:
echo.
echo   FastAPI Backend:    http://localhost:8000
echo   API Documentation:  http://localhost:8000/docs
echo   Flask AI Agent:     http://localhost:5000
echo   React Frontend:     http://localhost:5173
echo.
echo ===============================================================================
echo.
echo NEXT STEPS:
echo   1. Wait 10-15 seconds for all services to initialize
echo   2. Open browser: http://localhost:5173
echo   3. Click "Login" to register/login
echo   4. Start chatting with the AI assistant!
echo.
echo NEW FEATURES IN V2.0:
echo   - Multi-Item Orders (order multiple items at once)
echo   - Restaurant Reviews and Ratings (rate 1-5 stars)
echo   - Cuisine-Based Search (filter by Gujarati, Italian, etc.)
echo   - Enhanced AI Personality (emojis and friendly responses)
echo.
echo ===============================================================================
echo.
echo To stop all services: Close each terminal window individually
echo.
pause

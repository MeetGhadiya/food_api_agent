@echo off
echo ============================================================
echo FoodieExpress Agent - Test Suite Launcher
echo ============================================================
echo.

cd /d "%~dp0"

echo Checking agent status...
curl -s http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Agent is not running!
    echo.
    echo Please start the agent first:
    echo   cd food_chatbot_agent
    echo   python agent.py
    echo.
    pause
    exit /b 1
)

echo [OK] Agent is running on port 5000
echo.
echo ============================================================
echo Starting Comprehensive Test Suite...
echo ============================================================
echo.

.\.venv\Scripts\python.exe run_comprehensive_tests.py

echo.
echo ============================================================
echo Testing Complete!
echo ============================================================
echo.
echo Check the generated JSON report for detailed results.
echo.
pause

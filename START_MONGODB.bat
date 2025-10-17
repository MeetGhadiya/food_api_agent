@echo off
REM Start MongoDB Service - Windows
REM ================================

echo.
echo ========================================
echo   STARTING MONGODB SERVICE
echo ========================================
echo.

REM Try to start MongoDB as Windows Service
net start MongoDB 2>nul

if %errorlevel% == 0 (
    echo.
    echo [SUCCESS] MongoDB service started!
    echo.
) else (
    echo.
    echo [INFO] MongoDB service not found or already running
    echo.
    echo Checking if MongoDB is running...
    tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
    if "%ERRORLEVEL%"=="0" (
        echo [SUCCESS] MongoDB is already running!
    ) else (
        echo [WARNING] MongoDB is not running!
        echo.
        echo Please start MongoDB manually:
        echo   1. If installed as service: net start MongoDB
        echo   2. If installed standalone: mongod --dbpath="C:\data\db"
        echo   3. Or use Docker: docker run -d -p 27017:27017 mongo:latest
    )
)

echo.
echo ========================================
echo   RESTARTING FASTAPI BACKEND
echo ========================================
echo.
echo Please restart your backend manually:
echo   1. Press Ctrl+C in the terminal running uvicorn
echo   2. Run: cd food_api
echo   3. Run: python -m uvicorn app.main:app --reload
echo.
echo After restarting, try registration again!
echo.

pause

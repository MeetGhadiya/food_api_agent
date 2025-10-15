@echo off
REM ==========================================
REM FoodieExpress V4.0 - Docker Startup Script
REM ==========================================

echo.
echo ========================================
echo   FoodieExpress V4.0 - Docker Setup
echo ========================================
echo.

REM Check if Docker is running
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running or not installed!
    echo.
    echo Please:
    echo 1. Install Docker Desktop from https://www.docker.com/products/docker-desktop
    echo 2. Start Docker Desktop
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo.
    echo Creating .env from template...
    copy .env.example .env >nul 2>&1
    echo.
    echo [ACTION REQUIRED] Please edit .env file with your actual credentials:
    echo   - MONGODB_URI
    echo   - GOOGLE_API_KEY
    echo   - SECRET_KEY
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo [OK] .env file found
echo.

REM Stop existing containers
echo Stopping existing containers...
docker-compose down 2>nul

echo.
echo ========================================
echo   Building and Starting Services
echo ========================================
echo.
echo This may take a few minutes on first run...
echo.

REM Build and start services
docker-compose up --build

REM If user interrupts, clean up
:cleanup
echo.
echo ========================================
echo   Shutting Down Services
echo ========================================
docker-compose down
echo.
echo Goodbye!
pause

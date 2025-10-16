@echo off
echo ========================================
echo  FoodieExpress Test Suite Runner
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "..\..venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please create a virtual environment first.
    pause
    exit /b 1
)

echo Starting comprehensive test suite...
echo.

REM Run the tests
"..\.venv\Scripts\python.exe" run_comprehensive_tests.py

echo.
echo ========================================
echo  Tests Complete!
echo ========================================
pause

@echo off
REM Automated Test Runner for FoodieExpress API
REM Quick way to run all tests

echo ========================================
echo   FoodieExpress API - Automated Tests
echo ========================================
echo.

cd food_api

echo Running all tests...
echo.

python -m pytest -v --tb=short --color=yes tests/

echo.
echo ========================================
echo   Test Execution Complete
echo ========================================
echo.

pause

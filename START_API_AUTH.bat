@echo off
REM Start FastAPI Server with Authentication
echo.
echo ========================================
echo   STARTING FASTAPI SERVER
echo ========================================
echo.

cd food_api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause

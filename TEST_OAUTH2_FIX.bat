@echo off
echo ========================================
echo   TESTING OAUTH2 FIX
echo ========================================
echo.
echo Starting server in 3 seconds...
timeout /t 3 /nobreak > nul

start "FastAPI Server" cmd /k "cd food_api && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for server to start...
timeout /t 8 /nobreak > nul

echo.
echo Checking OpenAPI schema...
python check_openapi_schema.py

echo.
echo ========================================
echo If OAuth2 is GONE, the fix worked!
echo If OAuth2 is STILL THERE, we need to dig deeper.
echo ========================================
echo.
echo Press any key to open Swagger UI in browser...
pause > nul

start http://localhost:8000/docs

pause

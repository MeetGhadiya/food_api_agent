@echo off
cls
echo ========================================
echo   FINAL FIX: Manual Token Extraction
echo ========================================
echo.
echo Starting server...
cd food_api
start "FastAPI Server" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for server to start...
timeout /t 8 /nobreak > nul

echo.
echo Checking OpenAPI schema...
cd ..
python check_openapi_schema.py

echo.
echo ========================================
echo Opening Swagger UI in 3 seconds...
timeout /t 3 /nobreak > nul

start http://localhost:8000/docs

echo.
echo ========================================
echo   INSTRUCTIONS:
echo ========================================
echo.
echo 1. Hard refresh the page: Ctrl + Shift + R
echo.
echo 2. Click "Authorize" button (top-right)
echo.
echo 3. If you STILL see OAuth2 dialog:
echo    - The issue is with FastAPI auto-detection
echo    - We need to use a different approach
echo.
echo 4. If you see HTTPBearer dialog:
echo    - SUCCESS! Enter: Bearer [your_token]
echo.
pause

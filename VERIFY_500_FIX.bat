@echo off
cls
echo.
echo ========================================
echo   500 ERROR FIX - VERIFICATION
echo ========================================
echo.
echo Starting FastAPI server...
cd food_api
start "FastAPI Server" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for server to start...
timeout /t 8 /nobreak > nul

echo.
echo Testing both login endpoints...
cd ..
python test_login_fix.py

echo.
echo ========================================
echo   INSTRUCTIONS:
echo ========================================
echo.
echo 1. Check the test results above
echo.
echo 2. If both tests PASS, open Swagger:
echo    http://localhost:8000/docs
echo.
echo 3. Click "Authorize" button (top-right)
echo.
echo 4. Enter:
echo    username: MG9328
echo    password: Meet7805
echo.
echo 5. Click "Authorize"
echo.
echo 6. It should work now! No more 500 error!
echo.
echo ========================================
pause

start http://localhost:8000/docs

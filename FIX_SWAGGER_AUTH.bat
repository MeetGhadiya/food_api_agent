@echo off
echo.
echo ========================================
echo   QUICK FIX: Swagger Authorization
echo ========================================
echo.
echo The issue was: Old OAuth2 configuration conflicting with new Bearer token auth
echo.
echo FIXED:
echo  - Updated dependencies.py to use HTTPBearer
echo  - Removed OAuth2PasswordBearer
echo  - Added proper OpenAPI security scheme
echo  - Bearer token authentication now works correctly
echo.
echo ========================================
echo   HOW TO USE SWAGGER NOW:
echo ========================================
echo.
echo 1. Open browser: http://localhost:8000/docs
echo.
echo 2. First, login to get your token:
echo    - Click on POST /api/auth/login
echo    - Click "Try it out"
echo    - Enter:
echo      {
echo        "username_or_email": "MG9328",
echo        "password": "Meet7805"
echo      }
echo    - Click "Execute"
echo    - Copy the "token" value from the response
echo.
echo 3. Authorize in Swagger:
echo    - Click the "Authorize" button (top-right, green lock icon)
echo    - In the "Value" field, paste: Bearer YOUR_TOKEN_HERE
echo    - Click "Authorize"
echo    - Click "Close"
echo.
echo 4. Now you can test protected endpoints!
echo.
echo ========================================
echo   Starting API Server...
echo ========================================
echo.

cd food_api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause

@echo off
REM Start Frontend - No Authentication Version
REM ===========================================

echo.
echo ========================================
echo   STARTING FRONTEND (NO LOGIN)
echo ========================================
echo.

cd chatbot_frontend

echo [1/2] Cleaning cache...
if exist node_modules\.vite (
    rmdir /s /q node_modules\.vite
    echo     Cache cleared!
) else (
    echo     No cache to clear
)

echo.
echo [2/2] Starting Vite dev server...
echo.

call npm run dev

echo.
echo If the server doesn't start, press Ctrl+C and run this manually:
echo     cd chatbot_frontend
echo     npm run dev
echo.

pause

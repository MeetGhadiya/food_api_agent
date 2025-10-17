@echo off
REM Restart Frontend Server
REM ========================

echo.
echo ========================================
echo   RESTARTING FRONTEND SERVER
echo ========================================
echo.

echo [INFO] Stopping any running Vite servers...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *vite*" 2>nul

echo.
echo [INFO] Starting fresh frontend server...
echo.

cd chatbot_frontend
start cmd /k "npm run dev"

echo.
echo ========================================
echo   FRONTEND SERVER STARTING...
echo ========================================
echo.
echo The frontend will open in a new terminal window.
echo.
echo Once you see "Local: http://localhost:5173"
echo Then open: http://localhost:5173
echo.
echo The Login button should now be gone!
echo.

pause

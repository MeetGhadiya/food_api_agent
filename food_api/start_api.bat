@echo off
cd /d "%~dp0"
echo Starting FastAPI Backend...
"E:/agent workspace/agent/food_api_agent/.venv/Scripts/python.exe" -m uvicorn app.main:app --reload
pause

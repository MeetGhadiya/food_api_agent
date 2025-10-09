# Food Delivery AI Agent - Startup Script
# This script starts both the API backend and the web agent

Write-Host "🚀 Starting Food Delivery AI Agent System..." -ForegroundColor Cyan
Write-Host ""

# Start FastAPI Backend
Write-Host "📡 Starting FastAPI Backend on port 8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1\food_api'; C:/Users/Skill/Desktop/m/python.exe -m uvicorn app.main:app --reload"

# Wait a moment for the backend to start
Start-Sleep -Seconds 3

# Start Flask Web Agent
Write-Host "🌐 Starting Web Agent on port 5000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1\food_api_agent'; C:/Users/Skill/Desktop/m/python.exe web_agent.py"

# Wait a moment for the web agent to start
Start-Sleep -Seconds 3

# Open browser
Write-Host "🌍 Opening browser..." -ForegroundColor Green
Start-Process "http://localhost:5000"

Write-Host ""
Write-Host "✅ System Started Successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 API Backend: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "📍 Web Interface: http://localhost:5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C in each terminal window to stop the servers" -ForegroundColor Gray

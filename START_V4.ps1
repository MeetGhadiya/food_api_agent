# ==========================================
# FoodieExpress V4.0 - Quick Start Script
# Windows PowerShell
# ==========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FoodieExpress V4.0 - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "📋 Copying .env.example to .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit .env and add your credentials:" -ForegroundColor Yellow
    Write-Host "   - GOOGLE_API_KEY" -ForegroundColor Yellow
    Write-Host "   - MONGODB_URI" -ForegroundColor Yellow
    Write-Host "   - SECRET_KEY" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Press Enter after editing .env, or Ctrl+C to exit"
}

# Check if Docker is running
Write-Host "🔍 Checking Docker..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if Docker daemon is running
try {
    docker ps | Out-Null
    Write-Host "✅ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker daemon is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting FoodieExpress V4.0..." -ForegroundColor Cyan
Write-Host ""

# Start services with Docker Compose
docker-compose up --build

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 FoodieExpress V4.0 Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Services Available:" -ForegroundColor Cyan
Write-Host "   AI Agent:    http://localhost:5000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Redis:       localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Test backend: curl http://localhost:8000/health" -ForegroundColor White
Write-Host "   2. Test agent:   curl http://localhost:5000/health" -ForegroundColor White
Write-Host "   3. View API docs: Open http://localhost:8000/docs in browser" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop: Press Ctrl+C, then run: docker-compose down" -ForegroundColor Yellow
Write-Host ""

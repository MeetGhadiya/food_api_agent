#!/bin/bash

# ==========================================
# FoodieExpress V4.0 - Quick Start Script
# Linux/macOS Bash
# ==========================================

echo "========================================"
echo "  FoodieExpress V4.0 - Quick Start"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📋 Copying .env.example to .env..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your credentials:"
    echo "   - GOOGLE_API_KEY"
    echo "   - MONGODB_URI"
    echo "   - SECRET_KEY"
    echo ""
    read -p "Press Enter after editing .env, or Ctrl+C to exit..."
fi

# Check if Docker is installed
echo "🔍 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found!"
    echo "Please install Docker from: https://www.docker.com/get-started"
    exit 1
fi

DOCKER_VERSION=$(docker --version)
echo "✅ Docker installed: $DOCKER_VERSION"

# Check if Docker daemon is running
if ! docker ps &> /dev/null; then
    echo "❌ Docker daemon is not running!"
    echo "Please start Docker"
    exit 1
fi

echo "✅ Docker daemon is running"
echo ""
echo "🚀 Starting FoodieExpress V4.0..."
echo ""

# Start services with Docker Compose
docker-compose up --build

echo ""
echo "========================================"
echo "🎉 FoodieExpress V4.0 Started!"
echo "========================================"
echo ""
echo "🌐 Services Available:"
echo "   AI Agent:    http://localhost:5000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo "   Redis:       localhost:6379"
echo ""
echo "📚 Next Steps:"
echo "   1. Test backend: curl http://localhost:8000/health"
echo "   2. Test agent:   curl http://localhost:5000/health"
echo "   3. View API docs: Open http://localhost:8000/docs in browser"
echo ""
echo "🛑 To stop: Press Ctrl+C, then run: docker-compose down"
echo ""

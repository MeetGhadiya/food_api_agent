# ==========================================
# GitHub Merge Conflict Resolution Script
# FoodieExpress V4.0
# ==========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Merge Conflict Resolution Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔍 Analyzing conflicts..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Remove cached node_modules and __pycache__ from Git
Write-Host "📦 Step 1: Removing node_modules and __pycache__ from Git..." -ForegroundColor Yellow

Write-Host "   Removing chatbot_frontend/node_modules..." -ForegroundColor Gray
git rm -r --cached chatbot_frontend/node_modules 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Removed chatbot_frontend/node_modules" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Already removed or doesn't exist" -ForegroundColor Gray
}

Write-Host "   Removing food_api/app/__pycache__..." -ForegroundColor Gray
git rm -r --cached food_api/app/__pycache__ 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Removed food_api/app/__pycache__" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Already removed or doesn't exist" -ForegroundColor Gray
}

Write-Host "   Removing food_chatbot_agent/__pycache__..." -ForegroundColor Gray
git rm -r --cached food_chatbot_agent/__pycache__ 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Removed food_chatbot_agent/__pycache__" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Already removed or doesn't exist" -ForegroundColor Gray
}

Write-Host ""

# Step 2: Stage the updated .gitignore
Write-Host "📝 Step 2: Staging updated .gitignore..." -ForegroundColor Yellow
git add .gitignore
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ .gitignore staged" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to stage .gitignore" -ForegroundColor Red
}

Write-Host ""

# Step 3: Commit the changes
Write-Host "💾 Step 3: Committing changes..." -ForegroundColor Yellow
git commit -m "Fix: Remove node_modules and __pycache__ from Git tracking

- Added node_modules to .gitignore
- Removed cached node_modules and __pycache__ directories
- These files should never be in version control
- Resolves merge conflicts in dependency files"

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Changes committed" -ForegroundColor Green
} else {
    Write-Host "   ❌ Commit failed" -ForegroundColor Red
    Write-Host "   💡 You may need to resolve conflicts manually" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Instructions for pushing
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Conflict resolution complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📤 To push your changes:" -ForegroundColor Cyan
Write-Host "   git push origin MG" -ForegroundColor White
Write-Host ""
Write-Host "🔄 If you need to pull latest changes first:" -ForegroundColor Cyan
Write-Host "   git pull origin main --rebase" -ForegroundColor White
Write-Host "   git push origin MG" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   • node_modules and __pycache__ are now ignored" -ForegroundColor White
Write-Host "   • These won't cause conflicts anymore" -ForegroundColor White
Write-Host "   • Team members should delete their local copies" -ForegroundColor White
Write-Host ""
Write-Host "🆘 If you still have conflicts:" -ForegroundColor Yellow
Write-Host "   1. Check the GitHub PR for remaining conflicts" -ForegroundColor White
Write-Host "   2. Use 'git status' to see what needs resolution" -ForegroundColor White
Write-Host "   3. Manually edit conflicted files" -ForegroundColor White
Write-Host "   4. Use 'git add <file>' after resolving each" -ForegroundColor White
Write-Host "   5. Use 'git commit' to finalize" -ForegroundColor White
Write-Host ""

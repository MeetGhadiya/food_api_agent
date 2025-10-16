# Scan ALL commits in current branch for secrets
# Usage: .\check-all-commits.ps1
# Usage with base branch: .\check-all-commits.ps1 -BaseBranch "main"

param(
    [string]$BaseBranch = "main"
)

Write-Host "`n🔍 Scanning ALL commits in branch for secrets..." -ForegroundColor Cyan
Write-Host "Base branch: $BaseBranch`n" -ForegroundColor Gray

# Check if base branch exists
$branchExists = git rev-parse --verify $BaseBranch 2>$null
if (-not $branchExists) {
    Write-Host "⚠️  Base branch '$BaseBranch' not found. Scanning all commits instead.`n" -ForegroundColor Yellow
    $commits = git log --oneline
} else {
    # Get all commits not in base branch
    $commits = git log "$BaseBranch..HEAD" --oneline 2>$null
}

if (-not $commits) {
    Write-Host "✅ No commits to scan (branch is up to date with $BaseBranch)`n" -ForegroundColor Green
    exit 0
}

$commitCount = ($commits | Measure-Object).Count
Write-Host "📊 Found $commitCount commit(s) to scan`n" -ForegroundColor Yellow

$errors = @()
$warnings = @()

# Secret patterns to detect
$secretPatterns = @{
    "MongoDB Connection String" = "mongodb(\+srv)?://[^\s:]+:[^\s@]+@"
    "Generic Password" = "(password|passwd|pwd)\s*=\s*['\`"][^'\`"]+"
    "API Key" = "(api[_-]?key|apikey)\s*=\s*['\`"][A-Za-z0-9]{20,}"
    "AWS Secret Key" = "(aws_secret_access_key|AWS_SECRET_ACCESS_KEY)\s*=\s*['\`"][A-Za-z0-9/+]{40}"
    "Private Key" = "-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"
    "Bearer Token" = "Bearer\s+[A-Za-z0-9\-._~+/]+=*"
}

# Banned filenames
$bannedPatterns = @(
    "*CONNECTION_SUCCESS*.md",
    "*_CREDENTIALS*.md",
    "*_SECRETS*.md",
    "*_PASSWORD*.md",
    ".env"
)

# Check each commit
$currentCommit = 1
foreach ($commitLine in $commits) {
    $hash = ($commitLine -split " ", 2)[0]
    $message = ($commitLine -split " ", 2)[1]
    
    Write-Host "[$currentCommit/$commitCount] Checking: " -NoNewline -ForegroundColor Gray
    Write-Host "$hash" -NoNewline -ForegroundColor Cyan
    Write-Host " - $message" -ForegroundColor Gray
    
    # Get files changed in this commit
    $files = git diff-tree --no-commit-id --name-only -r $hash 2>$null
    
    if ($files) {
        foreach ($file in $files) {
            # Check banned filename patterns
            foreach ($pattern in $bannedPatterns) {
                if ($file -like $pattern) {
                    $errors += "❌ Banned file in commit $hash : $file"
                }
            }
            
            # Get file content at this commit
            $content = git show "${hash}:${file}" 2>$null
            
            if ($content) {
                # Check for secret patterns
                foreach ($patternName in $secretPatterns.Keys) {
                    $regex = $secretPatterns[$patternName]
                    if ($content -match $regex) {
                        $errors += "❌ Found $patternName in $hash - File: $file"
                    }
                }
                
                # Additional warnings for suspicious patterns
                if ($content -match "Meet7805") {
                    $warnings += "⚠️  Found 'Meet7805' (MongoDB password) in $hash - File: $file"
                }
                if ($content -match "SecurePass123|OrderPass123|ReviewPass123") {
                    $warnings += "⚠️  Found test password in $hash - File: $file"
                }
            }
        }
    }
    
    $currentCommit++
}

Write-Host ""

# Report results
if ($errors.Count -gt 0) {
    Write-Host "⛔ CRITICAL: SECRETS FOUND IN COMMIT HISTORY!`n" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host $error -ForegroundColor Yellow
    }
    
    Write-Host "`n🔧 How to fix:" -ForegroundColor Cyan
    Write-Host "  Option 1: Clean with git filter-repo (removes files from ALL commits)" -ForegroundColor White
    Write-Host "    git filter-repo --path FILENAME --invert-paths --force" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Option 2: Squash merge (hides commit history)" -ForegroundColor White
    Write-Host "    On GitHub PR: Use 'Squash and merge' button" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Option 3: Cherry-pick only clean commits" -ForegroundColor White
    Write-Host "    git cherry-pick CLEAN_COMMIT_HASH" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📖 Full guide: SAFE_MERGING_GUIDE.md`n" -ForegroundColor Cyan
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host "⚠️  WARNINGS:`n" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host $warning -ForegroundColor Yellow
    }
    Write-Host "`n💡 These might be old issues already fixed." -ForegroundColor Gray
    Write-Host "Consider cleaning commit history if merging to main branch.`n" -ForegroundColor Gray
}

Write-Host "✅ No active secrets detected in commits!" -ForegroundColor Green
Write-Host "Safe to merge (but check warnings above)`n" -ForegroundColor Gray

if ($warnings.Count -eq 0) {
    Write-Host "🎉 All clear! No secrets, no warnings.`n" -ForegroundColor Green
}

exit 0

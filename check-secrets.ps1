# Pre-commit Secret Scanner for Windows
# Run this manually before commits: .\check-secrets.ps1

Write-Host "`n🔍 Scanning for secrets..." -ForegroundColor Cyan

$errors = @()
$warnings = @()

# Get staged files
$stagedFiles = git diff --cached --name-only --diff-filter=ACM 2>$null

if (-not $stagedFiles) {
    Write-Host "❌ No files staged for commit." -ForegroundColor Yellow
    Write-Host "Run: git add <files>" -ForegroundColor White
    exit 0
}

Write-Host "Scanning $($stagedFiles.Count) file(s)...`n" -ForegroundColor Gray

# Banned filename patterns
$bannedPatterns = @(
    "*CONNECTION_SUCCESS*.md",
    "*_CREDENTIALS*.md",
    "*_SECRETS*.md",
    "*_PASSWORD*.md",
    "PRIVATE_*.md",
    "SECRET_*.md"
)

# Secret patterns to detect
$secretRegexes = @{
    "MongoDB Connection String" = "mongodb(\+srv)?://[^\s:]+:[^\s@]+@"
    "Generic Password Assignment" = "(password|passwd|pwd)\s*=\s*['\`"][^'\`"]+"
    "API Key Assignment" = "(api[_-]?key|apikey)\s*=\s*['\`"][A-Za-z0-9]{20,}"
    "AWS Secret Key" = "(aws_secret_access_key|AWS_SECRET_ACCESS_KEY)\s*=\s*['\`"][A-Za-z0-9/+]{40}"
    "Private Key" = "-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"
    "Bearer Token" = "Bearer\s+[A-Za-z0-9\-._~+/]+=*"
}

# Check each staged file
foreach ($file in $stagedFiles) {
    # Check banned filenames
    foreach ($pattern in $bannedPatterns) {
        if ($file -like $pattern) {
            $errors += "❌ Banned filename: $file (matches: $pattern)"
        }
    }
    
    # Check file content
    if (Test-Path $file) {
        $content = Get-Content $file -Raw -ErrorAction SilentlyContinue
        
        if ($content) {
            foreach ($secretName in $secretRegexes.Keys) {
                $pattern = $secretRegexes[$secretName]
                if ($content -match $pattern) {
                    $errors += "❌ Found $secretName in: $file"
                }
            }
            
            # Additional checks for .env files
            if ($file -match "\.env$" -and $file -notmatch "\.env\.example$") {
                $errors += "❌ Attempting to commit .env file: $file"
            }
        }
    }
}

# Report results
if ($errors.Count -gt 0) {
    Write-Host "⛔ SECRETS DETECTED - DO NOT COMMIT!`n" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host $error -ForegroundColor Yellow
    }
    Write-Host "`n📖 How to fix:" -ForegroundColor Cyan
    Write-Host "  1. Remove secrets from the files" -ForegroundColor White
    Write-Host "  2. Use .env files for credentials (and add .env to .gitignore)" -ForegroundColor White
    Write-Host "  3. Use placeholders in documentation (e.g., [YOUR_PASSWORD])" -ForegroundColor White
    Write-Host "`n💡 After fixing, run this script again" -ForegroundColor Cyan
    Write-Host "`nFiles with issues: $($errors.Count)`n" -ForegroundColor Red
    exit 1
}

Write-Host "✅ No secrets detected! Safe to commit.`n" -ForegroundColor Green
Write-Host "You can now run: git commit -m 'your message'`n" -ForegroundColor Gray
exit 0

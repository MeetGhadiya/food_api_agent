# 🔀 Safe Merging & Pull Request Guide

**Date**: October 16, 2025  
**Problem**: Security issues occur during merges/pull requests  
**Solution**: Pre-merge validation and safe practices

---

## 🚨 The Merge Problem

When you merge branches or create pull requests:
1. GitGuardian scans ALL commits in the PR
2. Even if files are deleted, old commits still have secrets
3. Secrets in ANY commit trigger alerts
4. You can't "unsee" secrets once they're in git history

---

## ✅ Safe Merge Workflow

### Option 1: Clean Branch Before Merging (Recommended)

**Before creating a PR or merging:**

```powershell
# 1. Switch to your feature branch
git checkout feature-branch

# 2. Run secret scanner on ALL commits
.\check-all-commits.ps1

# 3. If secrets found, clean the branch
git filter-repo --path FILENAME_WITH_SECRET.md --invert-paths --force

# 4. Re-add remote and force push
git remote add origin https://github.com/MeetGhadiya/food_api_agent.git
git push origin feature-branch --force

# 5. NOW create PR or merge
```

### Option 2: Squash Merge (Hides History)

**Squash all commits into one before merging:**

```powershell
# On GitHub PR:
# 1. Click "Squash and merge" instead of "Merge pull request"
# 2. This creates ONE new commit with all changes
# 3. Old commits with secrets are not in main branch history

# On command line:
git checkout main
git merge --squash feature-branch
git commit -m "Feature: description of changes"
git push
```

### Option 3: Cherry-Pick Clean Commits

**Only merge commits without secrets:**

```powershell
# 1. Identify clean commits
git log feature-branch --oneline

# 2. Cherry-pick only the clean ones
git checkout main
git cherry-pick COMMIT_HASH_1
git cherry-pick COMMIT_HASH_2

# 3. Push
git push
```

---

## 🛡️ Pre-Merge Checklist

Before ANY merge or pull request:

```powershell
# 1. Check current branch for secrets
.\check-secrets.ps1

# 2. Check ALL commits in branch (new script below)
.\check-all-commits.ps1

# 3. Verify no banned files exist
git ls-files | Select-String -Pattern "CONNECTION_SUCCESS|_CREDENTIALS|_SECRETS"

# 4. Check .gitignore is up to date
cat .gitignore | Select-String "\.env"

# 5. Verify .env is NOT in git
git ls-files | Select-String "\.env$"
# Should return nothing
```

---

## 📋 GitHub Pull Request Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Security Checklist ✅

Before merging, confirm:

- [ ] Ran `.\check-secrets.ps1` - No secrets in staged files
- [ ] Ran `.\check-all-commits.ps1` - No secrets in ANY commit
- [ ] No `.env` files committed
- [ ] No files matching `*CONNECTION_SUCCESS*.md` pattern
- [ ] All credentials use placeholders like `[YOUR_PASSWORD]`
- [ ] Used `.env.example` for setup documentation
- [ ] Reviewed MongoDB password is NOT in commits

## Changes Made

<!-- Describe your changes here -->

## Testing

<!-- How did you test these changes? -->
```

---

## 🔍 Branch Scanning Script

I'll create a script to scan ALL commits in a branch:

**File**: `check-all-commits.ps1`

```powershell
# Scan ALL commits in current branch for secrets
param(
    [string]$BaseBranch = "main"
)

Write-Host "`n🔍 Scanning ALL commits for secrets...`n" -ForegroundColor Cyan

# Get all commits not in base branch
$commits = git log $BaseBranch..HEAD --oneline

if (-not $commits) {
    Write-Host "✅ No commits to scan (branch is up to date with $BaseBranch)`n" -ForegroundColor Green
    exit 0
}

$commitCount = ($commits | Measure-Object).Count
Write-Host "Found $commitCount commit(s) to scan`n" -ForegroundColor Yellow

$errors = @()

# Secret patterns
$patterns = @{
    "MongoDB URI" = "mongodb(\+srv)?://[^\s:]+:[^\s@]+@"
    "Password" = "(password|passwd|pwd)\s*=\s*['\`"][^'\`"]+"
    "API Key" = "(api[_-]?key|apikey)\s*=\s*['\`"][A-Za-z0-9]{20,}"
}

# Check each commit
foreach ($commit in $commits) {
    $hash = ($commit -split " ")[0]
    $message = ($commit -split " ", 2)[1]
    
    Write-Host "Checking: $hash - $message" -ForegroundColor Gray
    
    # Get files changed in this commit
    $files = git diff-tree --no-commit-id --name-only -r $hash
    
    foreach ($file in $files) {
        # Get file content at this commit
        $content = git show "${hash}:${file}" 2>$null
        
        if ($content) {
            foreach ($patternName in $patterns.Keys) {
                if ($content -match $patterns[$patternName]) {
                    $errors += "❌ Found $patternName in commit $hash - file: $file"
                }
            }
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Host "`n⛔ SECRETS FOUND IN COMMIT HISTORY!`n" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host $error -ForegroundColor Yellow
    }
    Write-Host "`n🔧 To fix:" -ForegroundColor Cyan
    Write-Host "  Option 1: Clean the branch with git filter-repo" -ForegroundColor White
    Write-Host "  Option 2: Use squash merge to hide history" -ForegroundColor White
    Write-Host "  Option 3: Cherry-pick only clean commits`n" -ForegroundColor White
    exit 1
}

Write-Host "`n✅ No secrets found in any commits! Safe to merge.`n" -ForegroundColor Green
exit 0
```

---

## 🎯 GitHub Branch Protection Rules

Set up branch protection on GitHub:

1. Go to: **Repository → Settings → Branches**
2. Add rule for `main` branch:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require conversation resolution before merging
   - ✅ Require signed commits (optional)
   - ✅ Include administrators

---

## 🔄 Safe Merge Strategies

### Strategy 1: Feature Flags + Squash Merge
```powershell
# Work in feature branch
git checkout -b feature/new-feature

# Make commits (some might have mistakes)
git commit -am "work in progress"

# Before merging, squash everything
git checkout main
git merge --squash feature/new-feature
git commit -m "feat: add new feature (clean)"
git push

# Delete feature branch
git branch -D feature/new-feature
```

### Strategy 2: Rebase + Interactive Cleanup
```powershell
# Rebase your branch
git checkout feature-branch
git rebase -i main

# In editor, choose:
# - 'pick' for commits to keep
# - 'drop' for commits with secrets
# - 'squash' to combine commits

# Force push cleaned branch
git push origin feature-branch --force
```

### Strategy 3: Fresh Branch from Clean Commits
```powershell
# Create new clean branch
git checkout main
git checkout -b feature-clean

# Cherry-pick only clean commits
git cherry-pick GOOD_COMMIT_1
git cherry-pick GOOD_COMMIT_2

# Push clean branch
git push origin feature-clean

# Delete old dirty branch
git push origin --delete feature-branch
git branch -D feature-branch
```

---

## 📊 Merge Checklist Summary

| Check | Command | Expected Result |
|-------|---------|-----------------|
| No secrets in files | `.\check-secrets.ps1` | ✅ No secrets detected |
| No secrets in commits | `.\check-all-commits.ps1` | ✅ No secrets found |
| No .env files | `git ls-files \| grep "\.env$"` | Empty |
| No banned files | `git ls-files \| grep "CONNECTION_SUCCESS"` | Empty |
| .gitignore updated | `cat .gitignore` | Contains .env, credential patterns |

---

## 🚫 Common Merge Mistakes

### ❌ DON'T:
1. Merge without checking commit history
2. Create PR immediately after adding secrets
3. Assume deleting a file removes it from history
4. Use "Merge commit" if history has secrets
5. Skip the pre-merge checklist

### ✅ DO:
1. Run `.\check-all-commits.ps1` before merging
2. Use squash merge to hide messy history
3. Clean branches before creating PRs
4. Use branch protection rules
5. Review every commit in the PR

---

## 🆘 Emergency: Secret in PR

If GitGuardian alerts on a PR:

### Immediate Actions:
```powershell
# 1. DO NOT MERGE THE PR

# 2. Close the PR (don't merge)

# 3. Clean the branch
git checkout your-branch
git filter-repo --path FILE_WITH_SECRET.md --invert-paths --force

# 4. Force push
git remote add origin https://github.com/MeetGhadiya/food_api_agent.git
git push origin your-branch --force

# 5. If credentials were REAL (not test):
#    - Rotate the exposed credentials IMMEDIATELY
#    - See CRITICAL_SECURITY_MONGODB.md

# 6. Re-open PR (with clean history)
```

---

## 📖 Documentation Files

Create these in `.github/`:

1. **`.github/PULL_REQUEST_TEMPLATE.md`** - Security checklist
2. **`.github/ISSUE_TEMPLATE/security.md`** - Report security issues
3. **`.github/workflows/security-scan.yml`** - Auto-scan on PR (optional)

---

## 🎓 Best Practices for Teams

### Before Starting Work:
```powershell
# 1. Pull latest main
git checkout main
git pull

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Set up git hooks
# (Pre-commit hook automatically runs)
```

### During Development:
```powershell
# Before each commit:
.\check-secrets.ps1

# Commit only if clean
git commit -m "message"
```

### Before Merging:
```powershell
# 1. Check all commits
.\check-all-commits.ps1

# 2. If clean, create PR
# 3. Wait for review
# 4. Use "Squash and merge"
```

---

## 🔗 Related Files

- `check-secrets.ps1` - Scan staged files
- `check-all-commits.ps1` - Scan all commits (create this)
- `PREVENTION_SOLUTION.md` - Overall prevention guide
- `SECURITY_SUMMARY.md` - Security issue summary

---

## ✅ Quick Reference

**Before every merge:**
```powershell
# One command to check everything:
.\check-all-commits.ps1 && .\check-secrets.ps1 && echo "✅ Safe to merge"
```

---

**Created**: October 16, 2025  
**Purpose**: Prevent security issues during merges and pull requests  
**Status**: ✅ Ready to use

**Remember**: Prevention during merge is easier than cleanup after! 🛡️

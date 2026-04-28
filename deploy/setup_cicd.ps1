#!/usr/bin/env pwsh
# CI/CD Setup Script - GitHub + SSH Deploy Keys

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  CI/CD Setup - GitHub Repos + Deploy Keys" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: Generate SSH Deploy Key ---
$KEY_DIR = "$env:USERPROFILE\.ssh"
$KEY_FILE = "$KEY_DIR\github_deploy_key"

if (Test-Path $KEY_FILE) {
    Write-Host "[OK] Deploy key already exists: $KEY_FILE" -ForegroundColor Green
} else {
    Write-Host "[GENERATING] SSH deploy key..." -ForegroundColor Yellow
    if (-not (Test-Path $KEY_DIR)) {
        New-Item -ItemType Directory -Path $KEY_DIR -Force | Out-Null
    }
    ssh-keygen -t ed25519 -f $KEY_FILE -C "github-actions-deploy" -N '""'
    Write-Host "[OK] Key generated: $KEY_FILE" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== PUBLIC KEY (add to VPS servers) ===" -ForegroundColor Cyan
Get-Content "$KEY_FILE.pub"
Write-Host ""

# --- Step 2: Check git status for each project ---
$projects = @(
    @{ Name = "Sylectus";  Path = "$env:USERPROFILE\Sylectus";  Repo = "sylectus-bot" },
    @{ Name = "AmazonBOT"; Path = "$env:USERPROFILE\AmazonBOT"; Repo = "profit-pulse" },
    @{ Name = "ONYX";      Path = "$env:USERPROFILE\ONYX";      Repo = "onyx-platform" }
)

foreach ($proj in $projects) {
    Write-Host ""
    Write-Host "--------------------------------------" -ForegroundColor DarkGray
    Write-Host "Project: $($proj.Name)" -ForegroundColor Yellow

    if (-not (Test-Path $proj.Path)) {
        Write-Host "  [ERROR] Directory not found: $($proj.Path)" -ForegroundColor Red
        continue
    }

    Push-Location $proj.Path

    # Check if git repo
    $isGit = Test-Path ".git"
    if (-not $isGit) {
        Write-Host "  [INIT] Not a git repo. Initializing..." -ForegroundColor Yellow
        git init
        git add -A
        git commit -m "feat: initial commit"
    }

    # Check remote
    $remote = git remote -v 2>&1
    $hasOrigin = $remote | Select-String "origin"
    if ($hasOrigin) {
        Write-Host "  [OK] Remote already configured" -ForegroundColor Green
        $remote | ForEach-Object { Write-Host "       $_" }
    } else {
        $repoUrl = "git@github.com:duffyjennydcw777/$($proj.Repo).git"
        Write-Host "  [ADD] No remote. Adding origin: $repoUrl" -ForegroundColor Yellow
        git remote add origin $repoUrl
        Write-Host "  [OK] Remote added" -ForegroundColor Green
    }

    # Check branch
    $branch = git branch --show-current 2>&1
    if ($branch -ne "main") {
        Write-Host "  [RENAME] Current branch: $branch -> main" -ForegroundColor Yellow
        git branch -M main
    } else {
        Write-Host "  [OK] Branch: main" -ForegroundColor Green
    }

    # Check .gitignore for .env
    $gitignoreContent = Get-Content ".gitignore" -ErrorAction SilentlyContinue
    if ($gitignoreContent -match "\.env") {
        Write-Host "  [OK] .env is in .gitignore" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] .env NOT in .gitignore!" -ForegroundColor Red
    }

    # Show status
    $status = git status --porcelain
    $fileCount = ($status | Measure-Object).Count
    Write-Host "  [INFO] Uncommitted changes: $fileCount files"

    Pop-Location
}

# --- Step 3: Instructions ---
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Green
Write-Host "  NEXT STEPS (Manual - one time only)" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. CREATE REPOS on GitHub (private):" -ForegroundColor White
Write-Host "   github.com/new -> 'sylectus-bot' (private)" -ForegroundColor Gray
Write-Host "   github.com/new -> 'profit-pulse' (private)" -ForegroundColor Gray
Write-Host "   github.com/new -> 'onyx-platform' (private)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. ADD PUBLIC KEY to VPS servers:" -ForegroundColor White
Write-Host "   Sylectus (Hetzner):" -ForegroundColor Gray
Write-Host "     ssh root@65.109.58.108 `"echo '<KEY>' >> ~/.ssh/authorized_keys`"" -ForegroundColor Gray
Write-Host "   ONYX (Aeza):" -ForegroundColor Gray
Write-Host "     ssh root@92.246.137.35 -p 2222 `"echo '<KEY>' >> ~/.ssh/authorized_keys`"" -ForegroundColor Gray
Write-Host ""
Write-Host "3. ADD GITHUB SECRETS (per repo -> Settings -> Secrets):" -ForegroundColor White
Write-Host "   VPS_SSH_KEY       = private key content" -ForegroundColor Gray
Write-Host "   VPS_HOST          = server IP" -ForegroundColor Gray
Write-Host "   VPS_PORT          = 22 (Sylectus) or 2222 (ONYX)" -ForegroundColor Gray
Write-Host "   VPS_USER          = root" -ForegroundColor Gray
Write-Host "   TG_DEPLOY_TOKEN   = Telegram bot token" -ForegroundColor Gray
Write-Host "   TG_DEPLOY_CHAT    = Your Telegram chat ID" -ForegroundColor Gray
Write-Host ""
Write-Host "4. INITIAL PUSH:" -ForegroundColor White
Write-Host "   cd C:\Users\Gigabyte\Sylectus" -ForegroundColor Gray
Write-Host "   git add -A; git commit -m 'feat: add CI/CD'; git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "   cd C:\Users\Gigabyte\AmazonBOT" -ForegroundColor Gray
Write-Host "   git add -A; git commit -m 'feat: add CI/CD'; git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "   cd C:\Users\Gigabyte\ONYX" -ForegroundColor Gray
Write-Host "   git add -A; git commit -m 'feat: add CI/CD'; git push -u origin main" -ForegroundColor Gray
Write-Host ""

# Show private key if requested
if ($args -contains "-ShowPrivateKey") {
    Write-Host "=== PRIVATE KEY (for GitHub Secret VPS_SSH_KEY) ===" -ForegroundColor Red
    Get-Content $KEY_FILE
    Write-Host ""
}

Write-Host "To see the private key, re-run with: -ShowPrivateKey" -ForegroundColor DarkGray
Write-Host ""

$ErrorActionPreference = 'Stop'
$RepoUrl = 'https://github.com/jamilurrahmanjitu/API-Creact.git'
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TempRoot = Join-Path $env:TEMP 'heart-disease-api-github-publish'

Write-Host 'Checking Git installation...'
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is not installed. Install Git for Windows from https://git-scm.com/download/win, then run this script again.'
}

if (Test-Path $TempRoot) { Remove-Item $TempRoot -Recurse -Force }
Write-Host 'Cloning your GitHub repository. GitHub may ask you to sign in in your browser...'
git clone $RepoUrl $TempRoot
if ($LASTEXITCODE -ne 0) { throw 'Could not clone the repository. Check your internet connection and GitHub access.' }

$Files = @('app', 'model', 'Dockerfile', 'docker-compose.yml', 'requirements.txt', 'train_model.py', 'README.md', '.dockerignore', '.gitignore', 'render.yaml', 'publish_to_github.ps1')
foreach ($Item in $Files) {
    $Source = Join-Path $ProjectRoot $Item
    $Destination = Join-Path $TempRoot $Item
    if (Test-Path $Source) {
        if (Test-Path $Destination) { Remove-Item $Destination -Recurse -Force }
        Copy-Item $Source $Destination -Recurse -Force
    }
}

Push-Location $TempRoot
try {
    git add -A
    if ($LASTEXITCODE -ne 0) { throw 'Git could not stage the project files.' }
    git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host 'The GitHub repository already has the latest project files.'
    } else {
        git commit -m 'Add trained heart disease prediction API and Docker deployment'
        if ($LASTEXITCODE -ne 0) { throw 'Commit failed. Configure your Git name/email with git config and run this script again.' }
        git push origin main
        if ($LASTEXITCODE -ne 0) { throw 'Push failed. Complete GitHub sign-in/authorization and run this script again.' }
    }
} finally {
    Pop-Location
}

Write-Host ''
Write-Host 'GitHub upload completed.' -ForegroundColor Green
Write-Host 'Repository: https://github.com/jamilurrahmanjitu/API-Creact'
Write-Host 'Next: open https://render.com/deploy?repo=https://github.com/jamilurrahmanjitu/API-Creact and authorize Render.'

# run-dev.ps1 - Windows Development Launcher

# Set environment for all child processes
$repoRoot = Get-Location
$env:PYTHONPATH = "$($repoRoot.Path)\src"
$env:DATABASE_PATH = "$($repoRoot.Path)\data"
$env:OMNICORE_ENV = "development"

# Ensure data directory exists
if (-not (Test-Path $env:DATABASE_PATH)) {
    New-Item -ItemType Directory -Path $env:DATABASE_PATH | Out-Null
}

# Helper to start a backend service from repo root (keeps package imports working)
function Start-ServiceProcess {
    param(
        [Parameter(Mandatory = $true)][string]$ModulePath,
        [Parameter(Mandatory = $true)][int]$Port
    )
    $cmd = "cd `"$($repoRoot.Path)`"; python -m uvicorn $ModulePath`:app --port $Port --reload"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
}

# Start backend services in separate terminals (uvicorn imports via package path)
Start-ServiceProcess -ModulePath "core.roots.api" -Port 8001
Start-ServiceProcess -ModulePath "core.causality.api" -Port 8002
Start-ServiceProcess -ModulePath "core.epistemic.api" -Port 8003
Start-ServiceProcess -ModulePath "core.mmo.api" -Port 8004
Start-ServiceProcess -ModulePath "core.global_srv.api" -Port 8005
Start-ServiceProcess -ModulePath "core.gateway.api" -Port 8000

# Start frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$($repoRoot.Path)\src\frontend\omnicloud-ui`"; npm run dev"

Write-Host "All services starting..."
Write-Host "API Gateway: http://localhost:8000"
Write-Host "Dashboard:   http://localhost:3000"
Write-Host "API Docs:    http://localhost:8000/docs"

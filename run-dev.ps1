# run-dev.ps1 - Windows Development Launcher
$env:PYTHONPATH = (Get-Location).Path + "\src"
$env:DATABASE_PATH = (Get-Location).Path + "\data"
$env:OMNICORE_ENV = "development"

# Start backend services in separate terminals
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\core\roots; python -m uvicorn api:app --port 8001 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\core\causality; python -m uvicorn api:app --port 8002 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\core\epistemic; python -m uvicorn api:app --port 8003 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\core\mmo; python -m uvicorn api:app --port 8004 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\core\global_srv; python -m uvicorn api:app --port 8005 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\core\gateway; python -m uvicorn api:app --port 8000 --reload"

# Start frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src\frontend\omnicloud-ui; npm run dev"

Write-Host "All services starting..."
Write-Host "API Gateway: http://localhost:8000"
Write-Host "Dashboard:   http://localhost:3000"
Write-Host "API Docs:    http://localhost:8000/docs"
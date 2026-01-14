# Start Student Classification System
Write-Host "========================================"
Write-Host " Starting Student Classification System"
Write-Host "========================================"
Write-Host ""

# Start Backend in background
Write-Host "[1/2] Starting Backend API (port 5000)..."
$backendPath = Join-Path $PSScriptRoot "..\backend"
Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory $backendPath -WindowStyle Normal

# Wait for backend
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[2/2] Starting Frontend (port 8080)..."
Write-Host ""
Write-Host "========================================"
Write-Host " Frontend: http://localhost:8080"
Write-Host " Backend:  http://localhost:5000"
Write-Host "========================================"
Write-Host ""

Set-Location $PSScriptRoot
python -m http.server 8080

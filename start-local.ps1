# Krishi Mausam AI - local dev launcher (Windows)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Stopping old servers on ports 8000 and 5173..."
foreach ($port in 8000, 5173) {
  $connections = netstat -ano | Select-String ":$port\s"
  foreach ($line in $connections) {
    if ($line -match '\sLISTENING\s+(\d+)') {
      $procId = $Matches[1]
      if ($procId -and $procId -ne '0') {
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
      }
    }
  }
}

Start-Sleep -Seconds 1

Write-Host "Starting backend on http://127.0.0.1:8000 ..."
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$Root\backend'; uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
) | Out-Null

Start-Sleep -Seconds 2

Write-Host "Starting frontend on http://127.0.0.1:5173 ..."
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$Root\frontend'; npm run dev"
) | Out-Null

Start-Sleep -Seconds 4

try {
  $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 10
  Write-Host "Backend OK:" ($health | ConvertTo-Json -Compress)
} catch {
  Write-Host "Backend not ready yet. Wait a few seconds and open http://127.0.0.1:8000/api/health"
}

Write-Host ""
Write-Host "Open the app here:"
Write-Host "  http://127.0.0.1:5173"
Write-Host "  http://localhost:5173"
Write-Host ""
Write-Host "Keep both PowerShell windows open while testing."

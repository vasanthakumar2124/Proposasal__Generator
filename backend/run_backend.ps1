param([switch]$NoKill)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$py = Join-Path $PSScriptRoot "..\my_venv\Scripts\python.exe"
$log = Join-Path $PSScriptRoot "uvicorn.log"
$err = Join-Path $PSScriptRoot "uvicorn.err.log"

$conns = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($conns) {
    if ($NoKill) {
        Write-Output "Port 8000 is already in use. Run without -NoKill to replace it."
        exit 1
    }
    $conns | ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Output "Killed existing server(s) on port 8000."
}

Start-Process $py -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000' `
    -WorkingDirectory $PSScriptRoot -WindowStyle Hidden `
    -RedirectStandardOutput $log -RedirectStandardError $err

Start-Sleep -Seconds 8
$ok = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 8 -ErrorAction SilentlyContinue
if ($ok -and $ok.StatusCode -eq 200) {
    Write-Output "Server up: $($ok.Content)"
} else {
    Write-Output "Server failed to start. See $err"
    if (Test-Path $err) { Get-Content $err -Tail 20 }
    exit 1
}

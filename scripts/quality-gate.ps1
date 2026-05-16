param(
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$SkipBuild,
    [switch]$SkipE2E,
    [switch]$ResetDemo
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$LogDir = Join-Path $Root ".codex\logs"
$BackendPython = Join-Path $Backend ".venv\Scripts\python.exe"

if (-not (Test-Path $BackendPython)) {
    $BackendPython = "python"
}

if ([string]::IsNullOrWhiteSpace($env:DATABASE_URL)) {
    $env:DATABASE_URL = "sqlite:///./fitcoach-local.db"
}

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

function Invoke-GateStep {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    Write-Host ""
    Write-Host "==> $Name" -ForegroundColor Cyan
    $global:LASTEXITCODE = 0
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE."
    }
}

function Stop-NodeServerOnPort {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($connection in $connections) {
        $processId = $connection.OwningProcess
        if (-not $processId -or $processId -eq 0) {
            continue
        }

        $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        $name = if ($process) { $process.ProcessName } else { "" }
        $commandLine = if ($processInfo) { $processInfo.CommandLine } else { "" }

        if ($name -match "node|npm|cmd" -or $commandLine -match "next|npm run dev|playwright") {
            Write-Host "Stopping stale dev server on port $Port (PID $processId)." -ForegroundColor Yellow
            Stop-Process -Id $processId -Force
            continue
        }

        throw "Port $Port is already in use by PID $processId. Stop that process before running e2e."
    }
}

function Stop-BackendServerOnPort {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($connection in $connections) {
        $processId = $connection.OwningProcess
        if (-not $processId -or $processId -eq 0) {
            continue
        }

        $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
        $commandLine = if ($processInfo) { $processInfo.CommandLine } else { "" }

        if ($commandLine -match "uvicorn|app\.main:app|fastapi") {
            Write-Host "Stopping stale backend server on port $Port (PID $processId)." -ForegroundColor Yellow
            Stop-Process -Id $processId -Force
            continue
        }

        throw "Port $Port is already in use by PID $processId. Stop that process before running e2e."
    }
}

function Wait-Http {
    param(
        [string]$Url,
        [int]$Seconds = 45
    )

    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3 | Out-Null
            return
        }
        catch {
            Start-Sleep -Milliseconds 700
        }
    }

    throw "Timed out waiting for $Url."
}

Push-Location $Root
try {
    if ($ResetDemo) {
        Invoke-GateStep "Reset demo seed" {
            Push-Location $Backend
            try {
                & $BackendPython -m app.seed --reset-demo
            }
            finally {
                Pop-Location
            }
        }
    }

    if (-not $SkipBackend) {
        Invoke-GateStep "Backend tests" {
            Push-Location $Backend
            try {
                & $BackendPython -m pytest
            }
            finally {
                Pop-Location
            }
        }
    }

    if (-not $SkipFrontend) {
        Invoke-GateStep "Frontend lint" {
            Push-Location $Frontend
            try {
                npm run lint
            }
            finally {
                Pop-Location
            }
        }

        Invoke-GateStep "Frontend typecheck" {
            Push-Location $Frontend
            try {
                npm run typecheck
            }
            finally {
                Pop-Location
            }
        }

        Invoke-GateStep "Frontend unit tests" {
            Push-Location $Frontend
            try {
                npm run test
            }
            finally {
                Pop-Location
            }
        }

        if (-not $SkipBuild) {
            Invoke-GateStep "Frontend build" {
                Push-Location $Frontend
                try {
                    npm run build
                }
                finally {
                    Pop-Location
                }
            }
        }

        if (-not $SkipE2E) {
            Stop-BackendServerOnPort -Port 8000
            $backendOut = Join-Path $LogDir "quality-backend.out.log"
            $backendErr = Join-Path $LogDir "quality-backend.err.log"
            $script:backendProcess = $null
            Invoke-GateStep "Start backend for e2e" {
                $script:backendProcess = Start-Process `
                    -FilePath "powershell.exe" `
                    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "& '$BackendPython' -m uvicorn app.main:app --port 8000") `
                    -WorkingDirectory $Backend `
                    -WindowStyle Hidden `
                    -RedirectStandardOutput $backendOut `
                    -RedirectStandardError $backendErr `
                    -PassThru
                Wait-Http -Url "http://127.0.0.1:8000/health"
            }

            Stop-NodeServerOnPort -Port 3000
            try {
                Invoke-GateStep "Frontend e2e" {
                    Push-Location $Frontend
                    try {
                        npm run e2e
                    }
                    finally {
                        Pop-Location
                    }
                }
            }
            finally {
                if ($script:backendProcess -and -not $script:backendProcess.HasExited) {
                    Stop-Process -Id $script:backendProcess.Id -Force
                }
            }
        }
    }

    Write-Host ""
    Write-Host "Quality gate passed." -ForegroundColor Green
}
finally {
    Pop-Location
}

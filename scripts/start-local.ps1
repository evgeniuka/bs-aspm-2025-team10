param(
    [switch]$ResetDemo,
    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$LogDir = Join-Path $Root ".codex\logs"
$BackendEnv = Join-Path $Backend ".env"
$FrontendEnv = Join-Path $Frontend ".env.local"
$BackendPython = Join-Path $Backend ".venv\Scripts\python.exe"

if (-not (Test-Path $BackendPython)) {
    $BackendPython = "python"
}

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

function Invoke-Step {
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

function Get-EnvValue {
    param(
        [string]$Path,
        [string]$Name,
        [string]$Fallback
    )

    if (-not (Test-Path $Path)) {
        return $Fallback
    }

    $line = Get-Content $Path | Where-Object { $_ -match "^$Name=" } | Select-Object -First 1
    if (-not $line) {
        return $Fallback
    }

    return $line.Substring($Name.Length + 1).Trim()
}

function Set-Utf8NoBomContent {
    param(
        [string]$Path,
        [string]$Content
    )

    $encoding = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

function Test-PortOpen {
    param([int]$Port)
    return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
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

function Start-BackgroundService {
    param(
        [string]$Name,
        [string]$WorkingDirectory,
        [string]$Command,
        [string]$LogName
    )

    $stdout = Join-Path $LogDir "$LogName.out.log"
    $stderr = Join-Path $LogDir "$LogName.err.log"
    Write-Host "Starting $Name. Logs: $stdout / $stderr"
    Start-Process `
        -FilePath "powershell.exe" `
        -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $Command) `
        -WorkingDirectory $WorkingDirectory `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -PassThru | Out-Null
}

if (-not (Test-Path $BackendEnv)) {
    $secret = "$([Guid]::NewGuid().ToString("N"))$([Guid]::NewGuid().ToString("N"))"
    $content = @"
DATABASE_URL=sqlite:///./fitcoach-local.db
ENVIRONMENT=development
SECRET_KEY=$secret
FRONTEND_ORIGIN=http://localhost:3000,http://127.0.0.1:3000
SECURE_COOKIES=false
ACCESS_TOKEN_EXPIRE_MINUTES=1440
"@
    Set-Utf8NoBomContent -Path $BackendEnv -Content $content
}

if (-not (Test-Path $FrontendEnv)) {
    Copy-Item -Path (Join-Path $Frontend ".env.example") -Destination $FrontendEnv
}

if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
    throw "frontend\node_modules is missing. Run npm run setup:local first."
}

$DatabaseUrl = Get-EnvValue -Path $BackendEnv -Name "DATABASE_URL" -Fallback "sqlite:///./fitcoach-local.db"
$env:DATABASE_URL = $DatabaseUrl

Push-Location $Root
try {
    Invoke-Step "Prepare database" {
        Push-Location $Backend
        try {
            & $BackendPython -m alembic upgrade head
            if ($ResetDemo) {
                & $BackendPython -m app.seed --reset-demo
            } else {
                & $BackendPython -m app.seed
            }
        }
        finally {
            Pop-Location
        }
    }

    if (Test-PortOpen -Port 8000) {
        Write-Host "Backend already listens on http://127.0.0.1:8000."
    } else {
        Start-BackgroundService -Name "FastAPI backend" -WorkingDirectory $Backend -Command "& '$BackendPython' -m uvicorn app.main:app --reload --port 8000" -LogName "backend"
    }

    if (Test-PortOpen -Port 3000) {
        Write-Host "Frontend already listens on http://127.0.0.1:3000."
    } else {
        Start-BackgroundService -Name "Next.js frontend" -WorkingDirectory $Frontend -Command "npm run dev" -LogName "frontend"
    }

    Wait-Http -Url "http://127.0.0.1:8000/health"
    Wait-Http -Url "http://127.0.0.1:3000/login"

    if ($OpenBrowser) {
        Start-Process "http://127.0.0.1:3000/login"
    }

    Write-Host ""
    Write-Host "FitCoach Pro is running." -ForegroundColor Green
    Write-Host "Frontend: http://127.0.0.1:3000/login"
    Write-Host "Backend:  http://127.0.0.1:8000/health"
    Write-Host "Trainer:  trainer@fitcoach.dev / demo-password"
    Write-Host "Client:   maya@fitcoach.dev / demo-password"
}
finally {
    Pop-Location
}

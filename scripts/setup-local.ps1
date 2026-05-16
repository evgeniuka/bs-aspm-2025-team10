param(
    [switch]$UsePostgres,
    [switch]$SkipFrontendInstall
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$BackendEnv = Join-Path $Backend ".env"
$FrontendEnv = Join-Path $Frontend ".env.local"
$BackendPython = Join-Path $Backend ".venv\Scripts\python.exe"
$DatabaseUrl = if ($UsePostgres) {
    "postgresql+psycopg://fitcoach:fitcoach@localhost:5432/fitcoach"
} else {
    "sqlite:///./fitcoach-local.db"
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

function New-DevSecret {
    return "$([Guid]::NewGuid().ToString("N"))$([Guid]::NewGuid().ToString("N"))"
}

function Set-Utf8NoBomContent {
    param(
        [string]$Path,
        [string]$Content
    )

    $encoding = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

Push-Location $Root
try {
    Invoke-Step "Create backend virtual environment" {
        if (-not (Test-Path $BackendPython)) {
            Push-Location $Backend
            try {
                python -m venv .venv
            }
            finally {
                Pop-Location
            }
        } else {
            Write-Host "Backend virtual environment already exists."
        }
    }

    Invoke-Step "Install backend dependencies" {
        & $BackendPython -m pip install --upgrade pip
        & $BackendPython -m pip install -r (Join-Path $Backend "requirements.txt")
    }

    Invoke-Step "Create local backend .env" {
        if (-not (Test-Path $BackendEnv)) {
            $secret = New-DevSecret
            $content = @"
DATABASE_URL=$DatabaseUrl
ENVIRONMENT=development
SECRET_KEY=$secret
FRONTEND_ORIGIN=http://localhost:3000,http://127.0.0.1:3000
SECURE_COOKIES=false
ACCESS_TOKEN_EXPIRE_MINUTES=1440
"@
            Set-Utf8NoBomContent -Path $BackendEnv -Content $content
            Write-Host "Created backend\.env."
        } else {
            Write-Host "backend\.env already exists; leaving it untouched."
        }
    }

    Invoke-Step "Create local frontend .env.local" {
        if (-not (Test-Path $FrontendEnv)) {
            Copy-Item -Path (Join-Path $Frontend ".env.example") -Destination $FrontendEnv
            Write-Host "Created frontend\.env.local."
        } else {
            Write-Host "frontend\.env.local already exists; leaving it untouched."
        }
    }

    if (-not $SkipFrontendInstall) {
        Invoke-Step "Install frontend dependencies" {
            if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
                Push-Location $Frontend
                try {
                    npm install
                }
                finally {
                    Pop-Location
                }
            } else {
                Write-Host "frontend\node_modules already exists."
            }
        }
    }

    Invoke-Step "Run database migrations" {
        $env:DATABASE_URL = $DatabaseUrl
        Push-Location $Backend
        try {
            & $BackendPython -m alembic upgrade head
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Step "Seed demo workspace" {
        $env:DATABASE_URL = $DatabaseUrl
        Push-Location $Backend
        try {
            & $BackendPython -m app.seed --reset-demo
        }
        finally {
            Pop-Location
        }
    }

    Write-Host ""
    Write-Host "Local setup is ready." -ForegroundColor Green
    Write-Host "Start the app with: npm run start:local"
}
finally {
    Pop-Location
}

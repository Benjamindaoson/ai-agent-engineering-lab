param(
    [switch]$SetupOnly
)

$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
$AgentLab = Join-Path $Root "AI_Agent_Builder"
$VenvPython = Join-Path $AgentLab ".venv\Scripts\python.exe"
$Requirements = Join-Path $AgentLab "apps\api\requirements.txt"

function Invoke-Checked {
    param(
        [Parameter(Mandatory)] [string]$Label,
        [Parameter(Mandatory)] [scriptblock]$Command
    )

    Write-Host "== $Label =="
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE."
    }
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is required. Install Python 3.13+ and ensure 'python' is on PATH."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "Node.js/npm is required. Install Node.js and ensure 'npm' is on PATH."
}
if (-not (Test-Path -LiteralPath $AgentLab -PathType Container)) {
    throw "AgentLab directory not found: $AgentLab"
}

$CreatedVenv = -not (Test-Path -LiteralPath $VenvPython -PathType Leaf)
if ($CreatedVenv) {
    Invoke-Checked "Create Python virtual environment" { python -m venv (Join-Path $AgentLab ".venv") }
}

if ($CreatedVenv -or $SetupOnly) {
    Invoke-Checked "Install Python dependencies" { & $VenvPython -m pip install -r $Requirements }
}

$NodeModules = Join-Path $AgentLab "node_modules"
if (-not (Test-Path -LiteralPath $NodeModules -PathType Container)) {
    Push-Location $AgentLab
    try {
        Invoke-Checked "Install npm dependencies" { npm ci }
    }
    finally {
        Pop-Location
    }
}

Push-Location (Join-Path $AgentLab "apps\api")
try {
    Invoke-Checked "Seed local database" { & $VenvPython -m app.seed }
}
finally {
    Pop-Location
}

if ($SetupOnly) {
    Write-Host "Setup complete. Run .\run-local.ps1 to start AgentLab."
    exit 0
}

$Api = Start-Process `
    -FilePath $VenvPython `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--app-dir", "apps/api") `
    -WorkingDirectory $AgentLab `
    -WindowStyle Hidden `
    -PassThru

$NodeCommand = (Get-Command node).Source
$NextCli = Join-Path $AgentLab "node_modules\next\dist\bin\next"
$Web = Start-Process `
    -FilePath $NodeCommand `
    -ArgumentList @($NextCli, "dev", "--hostname", "127.0.0.1", "--port", "3000") `
    -WorkingDirectory (Join-Path $AgentLab "apps\web") `
    -WindowStyle Hidden `
    -PassThru

try {
    $Deadline = (Get-Date).AddSeconds(60)
    do {
        Start-Sleep -Milliseconds 500
        try {
            $Health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2
        }
        catch {
            $Health = $null
        }
    } until ($Health.status -eq "ok" -or (Get-Date) -ge $Deadline)

    if ($Health.status -ne "ok") {
        throw "AgentLab API did not become healthy within 60 seconds."
    }

    Write-Output "AgentLab is running."
    Write-Output "Web: http://127.0.0.1:3000"
    Write-Output "API: http://127.0.0.1:8000"
    Write-Output "API PID: $($Api.Id)"
    Write-Output "Web PID: $($Web.Id)"
    Write-Output "Stop: Stop-Process -Id $($Api.Id),$($Web.Id)"
}
catch {
    Stop-Process -Id $Api.Id,$Web.Id -Force -ErrorAction SilentlyContinue
    throw
}

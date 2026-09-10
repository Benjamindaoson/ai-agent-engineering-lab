$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
if (-not (Test-Path 'agentlab_web/node_modules')) { npm --prefix agentlab_web install }
npm --prefix agentlab_web run build
uv run python -m agentlab

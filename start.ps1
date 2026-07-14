Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$env:FASTMCP_LOG_LEVEL = 'WARNING'
# readly-mcp Start - Standards-Compliant SOTA
Write-Host 'Starting readly-mcp...' -ForegroundColor Cyan

Set-Location $PSScriptRoot

$WebPort = 10706
$BackendPort = 10863
$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath


Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList '-NoProfile', '-Command', "`$env:WEB_PORT = '$BackendPort'; uv run -m readly_mcp" -WindowStyle Hidden

Start-Sleep -Seconds 2

Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green
Set-Location web_sota
$env:VITE_API_TARGET = "http://127.0.0.1:$BackendPort"
$env:VITE_PORT = "$WebPort"
npm run dev -- --port $WebPort --host

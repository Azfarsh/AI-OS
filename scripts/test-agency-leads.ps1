# Agency Loop 1 test - lead pipeline
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$ais = "$Root\.venv\Scripts\ais.exe"

Write-Host "Running lead pipeline on sample leads..." -ForegroundColor Cyan
& $ais lead run

Write-Host ""
Write-Host "Lead files:" -ForegroundColor Cyan
& $ais lead list

Write-Host ""
Write-Host "Done. Open memory\leads\ for full lead records." -ForegroundColor Green

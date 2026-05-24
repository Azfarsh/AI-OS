# Quick smoke test - OpenRouter free models (requires OPENROUTER_API_KEY in .env)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "Config profile:"
& "$Root\.venv\Scripts\python.exe" -c "from ais_os.config import get_config; c=get_config(); print(c.config_profile, c.default_model, c.embed_provider)"

Write-Host ""
Write-Host "Agents list:"
& "$Root\.venv\Scripts\ais.exe" agents

Write-Host ""
Write-Host "Chat test (free router) - needs valid OPENROUTER_API_KEY in .env:"
& "$Root\.venv\Scripts\ais.exe" chat 'Reply with exactly: AIS-OS free test OK'

Write-Host ""
Write-Host "For full objective tests run: .\scripts\test-application.ps1"

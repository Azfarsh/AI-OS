# AIS-OS Windows setup
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "Creating virtual environment..."
python -m venv .venv
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env from .env.example — add OPENROUTER_API_KEY"
}

@("memory/notes", "memory/chroma", "sessions", "logs", "context") | ForEach-Object {
    $p = Join-Path $Root $_
    if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
}

Write-Host "Done. Run: .\.venv\Scripts\Activate.ps1 ; ais"
Write-Host "Or: python -m ais_os"

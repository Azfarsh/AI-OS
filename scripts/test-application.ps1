# AIS-OS objective-aligned test suite (terminal, free models)
# Run: .\scripts\test-application.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$py = "$Root\.venv\Scripts\python.exe"
$ais = "$Root\.venv\Scripts\ais.exe"
$passed = 0
$failed = 0

function Test-Step {
    param([string]$Name, [scriptblock]$Action)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "TEST: $Name" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    try {
        & $Action
        Write-Host "[PASS] $Name" -ForegroundColor Green
        $script:passed++
    }
    catch {
        Write-Host "[FAIL] $Name" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        $script:failed++
    }
}

Write-Host "AIS-OS Application Test Suite" -ForegroundColor Yellow
Write-Host "Workspace: $Root"

Test-Step "1. Config (free profile + local embeddings)" {
    $out = & $py -c "from ais_os.config import get_config; c=get_config(); assert c.config_profile=='free-test'; assert c.embed_provider=='local'; assert c.openrouter_api_key and c.openrouter_api_key!='sk-or-v1-your-key-here'; print('profile=',c.config_profile,'model=',c.default_model,'key=set')"
    Write-Host $out
}

Test-Step "2. Agents registry (9 agents)" {
    $out = & $py -c "from ais_os.agents.registry import get_agent_registry; n=len(get_agent_registry().list_agents()); assert n==9, n; print('agents=',n)"
    Write-Host $out
    & $ais agents
}

Test-Step "3. Smoke chat (exact reply)" {
    & $ais chat 'Reply with exactly: AIS-OS free test OK'
}

Test-Step "4. Context layer (agency 90-day goals from memory/context/)" {
    & $ais chat 'List the 3 ninety-day goals from agency_profile in memory/context. Reply as a numbered list only, no extra text.'
}

Test-Step "5. Agent routing - coding" {
    & $ais chat --agent coding_agent 'In one sentence: what Python file is the CLI entry point for this project?'
}

Test-Step "6. Agent routing - research" {
    & $ais chat --agent research_agent 'In 2 bullets: what is an AIOS Four Cs framework? Keep under 40 words.'
}

Test-Step "7. Memory write + search" {
    $tag = "test-" + (Get-Date -Format "yyyyMMdd-HHmmss")
    & $ais memory-save "AIS-OS memory test marker $tag"
    Start-Sleep -Seconds 2
    & $ais memory "AIS-OS memory test marker $tag"
}

Test-Step "8. Sessions list" {
    & $ais sessions
}

Test-Step "9. Config CLI" {
    & $ais config
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Results: $passed passed, $failed failed" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Interactive REPL:  ais" -ForegroundColor White
Write-Host "Try in REPL:" -ForegroundColor White
Write-Host "  /help" -ForegroundColor Gray
Write-Host "  /settings" -ForegroundColor Gray
Write-Host "  What should I focus on this week for the agency?" -ForegroundColor Gray
Write-Host "  /code list files in ais_os folder" -ForegroundColor Gray
Write-Host "  /memory save Client Acme prefers 1-page reports" -ForegroundColor Gray

if ($failed -gt 0) { exit 1 }
exit 0

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
Set-Location -LiteralPath $repoRoot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Sleeperplan Health Check" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$passed = $true

# 1. Check Python executable
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $pyVer = & $venvPython --version
    Write-Host "[OK] Virtual environment Python: $pyVer ($venvPython)" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Virtual environment not found at .venv" -ForegroundColor Red
    $passed = $false
}

# 2. Check installed dependencies
$checkDeps = "import sleeperplan, reportlab, pytest; print(f'sleeperplan {sleeperplan.__version__} | reportlab {reportlab.__version__} | pytest {pytest.__version__}')"
try {
    $depOutput = & $venvPython -c $checkDeps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Dependencies verified: $depOutput" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Dependency check failed: $depOutput" -ForegroundColor Red
        $passed = $false
    }
} catch {
    Write-Host "[FAIL] Failed running dependency check: $_" -ForegroundColor Red
    $passed = $false
}

# 3. Run Pytest Suite
Write-Host "`nRunning test suite..." -ForegroundColor Yellow
$pytestExe = Join-Path $repoRoot ".venv\Scripts\pytest.exe"
if (Test-Path $pytestExe) {
    & $pytestExe -q --tb=short
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] All unit tests passed" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Test failures detected" -ForegroundColor Red
        $passed = $false
    }
} else {
    Write-Host "[FAIL] pytest executable not found" -ForegroundColor Red
    $passed = $false
}

# 4. CLI Plan Smoke Test
Write-Host "`nChecking CLI draft validation gate..." -ForegroundColor Yellow
$sleeperplanExe = Join-Path $repoRoot ".venv\Scripts\sleeperplan.exe"
& $sleeperplanExe check (Join-Path $repoRoot "examples\neighbour.json") --as-of 2026-09-06 | Out-Null
if ($LASTEXITCODE -eq 3) {
    Write-Host "[OK] Review gate correctly identified draft status (exit code 3)" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Unexpected review gate exit code: $LASTEXITCODE" -ForegroundColor Red
    $passed = $false
}

Write-Host "==========================================" -ForegroundColor Cyan
if ($passed) {
    Write-Host " ALL HEALTH CHECKS PASSED: READY FOR WORK" -ForegroundColor Green
    exit 0
} else {
    Write-Host " HEALTH CHECKS FAILED" -ForegroundColor Red
    exit 1
}

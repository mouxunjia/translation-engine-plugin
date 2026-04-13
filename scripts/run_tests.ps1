# Translation Engine Plugin - Test Runner Script

param(
    [string]$TestPath = "tests",
    [switch]$Coverage,
    [switch]$Verbose
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Translation Engine Plugin - Running Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Set environment variable
$env:PYTHONPATH = $PSScriptRoot

# Install dependencies
Write-Host "`nInstalling test dependencies..." -ForegroundColor Yellow
pip install pytest pytest-asyncio pytest-cov -q

# Run tests
$pytestArgs = @($TestPath, "-v", "--tb=short")

if ($Coverage) {
    $pytestArgs += "--cov=plugin"
    $pytestArgs += "--cov-report=html"
    $pytestArgs += "--cov-report=term"
}

if ($Verbose) {
    $pytestArgs += "--log-cli-level=INFO"
}

Write-Host "`nRunning: pytest $pytestArgs" -ForegroundColor Yellow
pytest $pytestArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[PASS] All tests passed!" -ForegroundColor Green
} else {
    Write-Host "`n[FAIL] Some tests failed" -ForegroundColor Red
}

exit $LASTEXITCODE

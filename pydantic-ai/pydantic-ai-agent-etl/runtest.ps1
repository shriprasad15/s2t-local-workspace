param(
    [switch]$help = $false,
    [switch]$list = $false,
    [string]$run = ""
)

function Show-Help {
    Write-Host "`nTest Runner Help"
    Write-Host "================"
    Write-Host "Usage: .\run.ps1 [-help] [-list] [-run <test_pattern>]"
    Write-Host "`nOptions:"
    Write-Host "  -help         Show this help message"
    Write-Host "  -list         List all available tests"
    Write-Host "  -run          Run specific tests (e.g., 'test_insert_document or test_get_documents')"
    Write-Host "  (no options)  Run all tests`n"
}

# Show help if requested
if ($help) {
    Show-Help
    exit 0
}

# Create virtual environment if not exists
if (-not (Test-Path "venv")) {
    python -m venv venv
}

# Activate virtual environment
./venv/Scripts/Activate

# Install required packages
# pip install -r requirements-test.txt
pip install pytest requests pytest-cov pydantic pytest-asyncio

# Handle different execution modes
if ($list) {
    pytest tests/test_api_client.py --collect-only -q
}
elseif ($run) {
    pytest tests/test_api_client.py -v -k "$run"
}
else {
    pytest tests/test_api_client.py -v
}

# Deactivate virtual environment
deactivate
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Info { param([string]$s) Write-Host $s }
function Write-Warn { param([string]$s) Write-Host $s -ForegroundColor Yellow }
function Write-Err  { param([string]$s) Write-Host $s -ForegroundColor Red }

Write-Info "Scatterplot Printer (Word) setup"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

function Assert-Python {
    try {
        $ver = & python --version 2>$null
        if (-not $ver) { throw "Python not found" }
        Write-Info "Using $ver"
    } catch {
        Write-Err "Python was not found in PATH."
        Write-Info "Fix: Install Python 3.10/3.11 (Microsoft Store or python.org installer)."
        Write-Info "Then re-run this script."
        exit 1
    }
}

function Ensure-Venv {
    if (-not (Test-Path ".\\venv")) {
        Write-Info "Creating venv..."
        & python -m venv venv
    }
    Write-Info "Activating venv..."
    . .\\venv\\Scripts\\Activate.ps1
}

function Install-Requirements {
    Write-Info "Installing dependencies..."
    & python -m pip install --upgrade pip
    & pip install -r requirements.txt
}

function Install-PyInstaller {
    Write-Info "Installing PyInstaller..."
    & pip install pyinstaller
}

function Build-Exe {
    Write-Info "Building EXE..."
    & pyinstaller --onefile --noconsole --name scatterplot_printer --add-data "config.json;." --add-data "file-list.json;." word_printer.py
    Write-Info "EXE built at .\\dist\\scatterplot_printer.exe"
}

try {
    Assert-Python
    Ensure-Venv
    Install-Requirements

    if ($args -contains "--build-exe") {
        Install-PyInstaller
        Build-Exe
    } else {
        Write-Info "Setup complete."
        Write-Info "Run: python word_printer.py"
        Write-Info "Or build an EXE later with: .\\setup_windows.ps1 --build-exe"
    }
} catch {
    $msg = $_.Exception.Message
    Write-Err "Setup failed: $msg"

    if ($msg -match "ExecutionPolicy") {
        Write-Info "Fix: Run PowerShell as your user and execute:"
        Write-Info "  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned"
    } elseif ($msg -match "pip" -or $msg -match "wheel" -or $msg -match "certificate") {
        Write-Info "Fix: Check internet access and try again."
        Write-Info "If your network blocks pip, ask IT to allow python.org and pypi.org."
    } elseif ($msg -match "pywin32") {
        Write-Info "Fix: Re-run the script, or install directly:"
        Write-Info "  pip install pywin32"
    } elseif ($msg -match "pyinstaller") {
        Write-Info "Fix: Re-run with:"
        Write-Info "  pip install pyinstaller"
    } elseif ($msg -match "not recognized") {
        Write-Info "Fix: Close and reopen PowerShell so PATH updates, then rerun."
    } else {
        Write-Info "Fix: Re-run in PowerShell and send the error output if it persists."
    }
    exit 1
}

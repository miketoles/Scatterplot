Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Scatterplot Printer (Word) setup"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if (-not (Test-Path ".\\venv")) {
    Write-Host "Creating venv..."
    python -m venv venv
}

Write-Host "Activating venv..."
. .\\venv\\Scripts\\Activate.ps1

Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

if ($args -contains "--build-exe") {
    Write-Host "Installing PyInstaller..."
    pip install pyinstaller
    Write-Host "Building EXE..."
    pyinstaller --onefile --noconsole --name scatterplot_printer --add-data "config.json;." --add-data "file-list.json;." word_printer.py
    Write-Host "EXE built at .\\dist\\scatterplot_printer.exe"
} else {
    Write-Host "Setup complete."
    Write-Host "Run: python word_printer.py"
    Write-Host "Or build an EXE later with: .\\setup_windows.ps1 --build-exe"
}

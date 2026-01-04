<#
windows_build.ps1

Usage: run this from the `word-variant` folder on a fresh Windows machine (PowerShell)

This script attempts a no-admin install of Python 3.12.x (per-user), creates a venv,
installs dependencies, runs pywin32 post-install, and builds `word_printer.exe` with PyInstaller.

Notes:
- It prefers the official python.org installer with InstallAllUsers=0 so admin is not required.
- If the installer cannot run due to policy, the script will abort and print manual fallback steps.
- Run PowerShell as a normal user (NOT elevated).
#>

param(
    [string]$PythonVersion = '3.12.10',
    [string]$InstallerUrl = '',
    [switch]$SkipDownload
)

set -e
function Write-Log { param($s) Write-Host $s; Add-Content -Path build.log -Value ((Get-Date).ToString('o') + ' - ' + $s) }

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Log "Starting build in $scriptDir"

if (Test-Path build.log) { Remove-Item build.log -ErrorAction SilentlyContinue }

# 1) Locate existing python
function Find-PythonExe {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $cmd = Get-Command py -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    # common per-user install location
    $p = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
    if (Test-Path $p) { return $p }
    return $null
}

$pythonExe = Find-PythonExe
if ($pythonExe) {
    Write-Log "Found existing python at $pythonExe"
} else {
    Write-Log "Python not found — downloading python $PythonVersion installer"
    if (-not $InstallerUrl -or $InstallerUrl -eq '') {
        $InstallerUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe"
    }
    $installer = Join-Path $env:TEMP "python-installer-$PythonVersion.exe"
    if (-not $SkipDownload) {
        Write-Log "Downloading $InstallerUrl to $installer"
        try {
            Invoke-WebRequest -Uri $InstallerUrl -OutFile $installer -UseBasicParsing -ErrorAction Stop
        } catch {
            Write-Log "Download failed: $($_.Exception.Message)"
            Write-Log "Cannot proceed automatically. Please download Python from https://www.python.org/downloads/windows/ and re-run this script."
            exit 1
        }
    }

    # Run installer silently for current user
    $args = '/quiet','InstallAllUsers=0','PrependPath=1','Include_pip=1'
    Write-Log "Running installer (no admin): $installer $($args -join ' ')"
    $proc = Start-Process -FilePath $installer -ArgumentList $args -Wait -PassThru -NoNewWindow
    if ($proc.ExitCode -ne 0) {
        Write-Log "Installer returned exit code $($proc.ExitCode). If this failed due to policy, download and run the official installer manually or use another machine to build the EXE."
        exit 1
    }

    # try to locate python again
    $pythonExe = Find-PythonExe
    if (-not $pythonExe) {
        Write-Log "Python was installed but not found on PATH. Trying common location..."
        $p = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
        if (Test-Path $p) { $pythonExe = $p }
    }

    if (-not $pythonExe) {
        Write-Log "Failed to locate python after installation. Exiting."
        exit 1
    }
    Write-Log "Installed python located at $pythonExe"
}

# 2) Create venv
$venvDir = Join-Path $scriptDir 'venv'
if (-not (Test-Path $venvDir)) {
    Write-Log "Creating venv in $venvDir"
    & "$pythonExe" -m venv "$venvDir"
} else { Write-Log "venv already exists at $venvDir" }

$venvPython = Join-Path $venvDir 'Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Write-Log "Venv python not found at $venvPython — aborting"; exit 1
}

Write-Log "Upgrading pip and installing dependencies"
& "$venvPython" -m pip install --upgrade pip setuptools wheel
& "$venvPython" -m pip install -r requirements.txt
& "$venvPython" -m pip install pyinstaller

Write-Log "Running pywin32 postinstall (may require minor registration)"
try {
    & "$venvPython" -c "import pywin32_postinstall; pywin32_postinstall.install()"
} catch {
    Write-Log "pywin32 postinstall failed: $($_.Exception.Message) (continuing)"
}

# 3) Build EXE
Write-Log "Building word_printer.exe with PyInstaller"
# ensure logs folder exists
New-Item -ItemType Directory -Force -Path (Join-Path $scriptDir 'logs') | Out-Null

$specArgs = @(
    '--onefile',
    '--noconsole',
    '--add-data', 'config.json;.',
    '--add-data', 'file-list.json;.',
    '--add-data', 'logs;logs'
)

try {
    & "$venvPython" -m PyInstaller @specArgs word_printer.py
} catch {
    Write-Log "PyInstaller build failed: $($_.Exception.Message)"
    Write-Log "Try rebuilding with hidden import for win32timezone:"
    Write-Log "  & \"$venvPython\" -m PyInstaller --onefile --noconsole --hidden-import=win32timezone --add-data \"config.json;.\" --add-data \"file-list.json;.\" --add-data \"logs;logs\" word_printer.py"
    exit 1
}

if (Test-Path (Join-Path $scriptDir 'dist\word_printer.exe')) {
    Write-Log "Build succeeded: dist\word_printer.exe"
    Write-Log "You can copy dist\word_printer.exe plus config.json and file-list.json to target machines." 
} else {
    Write-Log "Build completed but dist\word_printer.exe not found — check PyInstaller output above."
}

Write-Log "Done. See build.log for details."

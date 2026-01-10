@echo off
REM ============================================================
REM  SCATTERPLOT PRINTER - ONE-CLICK INSTALLER
REM  Double-click this file to install everything automatically
REM ============================================================
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ============================================================
echo   SCATTERPLOT PRINTER INSTALLER
echo ============================================================
echo.

REM Check if already installed (EXE exists)
if exist "%~dp0dist\scatterplot_printer.exe" (
    echo Already installed! Launching app...
    start "" "%~dp0dist\scatterplot_printer.exe"
    goto :end
)

REM Check for Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Attempting to install...
    echo.

    REM Try winget first (Windows 10/11)
    where winget >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        echo Installing Python via Windows Package Manager...
        winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
        if !ERRORLEVEL! NEQ 0 (
            echo.
            echo Winget installation failed. Please install Python manually:
            echo   1. Go to https://www.python.org/downloads/
            echo   2. Download Python 3.11 or later
            echo   3. Run installer - CHECK "Add Python to PATH"
            echo   4. Re-run this INSTALL.bat
            echo.
            pause
            exit /b 1
        )
        echo.
        echo Python installed! Restarting installer...
        echo.
        REM Refresh PATH and restart
        start "" "%~dp0INSTALL.bat"
        exit /b 0
    ) else (
        echo.
        echo Windows Package Manager (winget) not available.
        echo Please install Python manually:
        echo   1. Go to https://www.python.org/downloads/
        echo   2. Download Python 3.11 or later
        echo   3. Run installer - CHECK "Add Python to PATH"
        echo   4. Re-run this INSTALL.bat
        echo.
        pause
        exit /b 1
    )
)

REM Python found - show version
echo Found Python:
python --version
echo.

REM Create virtual environment if needed
if not exist "%~dp0venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate venv and install dependencies
echo Installing dependencies...
call "%~dp0venv\Scripts\activate.bat"

python -m pip install --upgrade pip --quiet
pip install pywin32 pyinstaller --quiet
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Failed to install dependencies. Check your internet connection.
    pause
    exit /b 1
)

echo Dependencies installed.
echo.

REM Build the EXE
echo Building application...
pyinstaller --onefile --noconsole --name scatterplot_printer word_printer.py --distpath "%~dp0dist" --workpath "%~dp0build" --specpath "%~dp0build" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Build failed. Trying verbose mode...
    pyinstaller --onefile --noconsole --name scatterplot_printer word_printer.py --distpath "%~dp0dist" --workpath "%~dp0build" --specpath "%~dp0build"
    pause
    exit /b 1
)

REM Copy config files next to EXE
if exist "%~dp0config.json" copy /Y "%~dp0config.json" "%~dp0dist\" >nul
if exist "%~dp0file-list.json" copy /Y "%~dp0file-list.json" "%~dp0dist\" >nul

echo.
echo ============================================================
echo   INSTALLATION COMPLETE!
echo ============================================================
echo.
echo The app is ready at: %~dp0dist\scatterplot_printer.exe
echo.

REM Create desktop shortcut
echo Creating desktop shortcut...
set SCRIPT="%TEMP%\create_shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\Scatterplot Printer.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0dist\scatterplot_printer.exe" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0dist" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

echo Desktop shortcut created!
echo.

REM Launch the app
echo Launching Scatterplot Printer...
start "" "%~dp0dist\scatterplot_printer.exe"

:end
echo.
echo You can close this window.
timeout /t 5

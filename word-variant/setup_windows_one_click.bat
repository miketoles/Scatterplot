@echo off
setlocal
cd /d "%~dp0"

echo Scatterplot Printer (Word) setup
echo Running PowerShell installer...

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_windows.ps1" --build-exe %*
set EXITCODE=%ERRORLEVEL%

if not "%EXITCODE%"=="0" (
  echo.
  echo Setup failed with code %EXITCODE%.
  echo If you see ExecutionPolicy errors, open PowerShell and run:
  echo   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  echo Then re-run this file.
  pause
  exit /b %EXITCODE%
)

echo.
echo Installed! Run the Scatterplot Printer icon from your desktop.
pause

@echo off
setlocal

echo ============================================
echo  NRT Scatterplot Creator - Installer
echo ============================================
echo.

:: Set target directory
set "TARGET=%LOCALAPPDATA%\Programs\NRT Scatterplot Creator"

:: Check if app is running
tasklist /FI "IMAGENAME eq NRT Scatterplot Creator.exe" 2>nul | find /I "NRT Scatterplot Creator.exe" >nul
if not errorlevel 1 (
    echo.
    echo ERROR: NRT Scatterplot Creator is currently running.
    echo Please close the application and try again.
    echo.
    pause
    exit /b 1
)

:: Check if already installed
if exist "%TARGET%\NRT Scatterplot Creator.exe" (
    echo Found existing installation at:
    echo %TARGET%
    echo.
    choice /c YN /m "Overwrite existing installation"
    if errorlevel 2 (
        echo Installation cancelled.
        pause
        exit /b 0
    )
    echo.
    echo Removing old installation...
    rmdir /s /q "%TARGET%" 2>nul
)

:: Create target directory
echo Creating installation directory...
mkdir "%TARGET%" 2>nul

:: Copy files (exclude install.bat itself)
echo Copying application files...
echo This may take a moment...
echo.

:: Copy all files and folders except install.bat
for %%F in (*) do (
    if /i not "%%F"=="install.bat" (
        copy "%%F" "%TARGET%\" >nul 2>&1
    )
)

:: Copy subdirectories
for /d %%D in (*) do (
    xcopy "%%D" "%TARGET%\%%D\" /E /I /Q >nul 2>&1
)

:: Verify installation
if not exist "%TARGET%\NRT Scatterplot Creator.exe" (
    echo.
    echo ERROR: Installation failed. Could not copy files.
    echo Please make sure you extracted the full zip file.
    pause
    exit /b 1
)

:: Create desktop shortcut using PowerShell
echo Creating desktop shortcut...
set "SHORTCUT=%USERPROFILE%\Desktop\NRT Scatterplot Creator.lnk"
set "EXEPATH=%TARGET%\NRT Scatterplot Creator.exe"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%EXEPATH%'; $s.WorkingDirectory = '%TARGET%'; $s.Description = 'NRT Scatterplot Creator'; $s.Save()"

if exist "%SHORTCUT%" (
    echo Desktop shortcut created successfully.
) else (
    echo Note: Could not create desktop shortcut automatically.
    echo You can create one manually pointing to:
    echo %EXEPATH%
)

echo.
echo ============================================
echo  Installation Complete!
echo ============================================
echo.
echo Installed to: %TARGET%
echo.
echo You can now run the app from:
echo   - The desktop shortcut
echo   - Or: %EXEPATH%
echo.
echo Data will be stored on the network share:
echo   L:\BI Program Behavior Plans\Scatterplot Creator Data\
echo.
pause

@echo off
REM Helper to run the EXE or fallback to the Python script
setlocal
set MYDIR=%~dp0
) if exist "%MYDIR%dist\scatterplot_printer.exe" (
  echo Running bundled EXE...
  "%MYDIR%dist\scatterplot_printer.exe"
) else if exist "%MYDIR%scatterplot_printer.exe" (
  echo Running EXE in current folder...
  "%MYDIR%scatterplot_printer.exe"
) else (
  echo Bundled EXE not found; attempting to run Python script
  if exist "%MYDIR%venv\Scripts\activate.bat" (
    call "%MYDIR%venv\Scripts\activate.bat"
  )
  python "%MYDIR%word_printer.py"
)
pause

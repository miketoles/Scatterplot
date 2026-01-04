# Building `scatterplot_printer.exe` (no-admin, reproducible)

These steps are for building the one-file Windows EXE from `word_printer.py` on a Windows machine. None of the steps require administrator privileges if you install Python per-user (Microsoft Store or user installer) and use a virtual environment.

1) Prepare Windows machine

- Install Python 3.10/3.11 from the Microsoft Store (per-user) or the official installer choosing "Install for me only". Verify with:

```powershell
python --version
```

2) Create and activate a virtual environment (recommended)

```powershell
cd C:\path\to\word-variant
python -m venv venv
venv\Scripts\Activate.ps1   # PowerShell
# or venv\Scripts\activate.bat  # cmd.exe
pip install --upgrade pip
```

3) Install build/runtime dependencies

```powershell
pip install pywin32
pip install pyinstaller
```

4) Build the EXE with PyInstaller

Run PyInstaller from the `word-variant` folder. Include `config.json` and `file-list.json` as data files so the EXE can pick them up when colocated.

```powershell
# produce `scatterplot_printer.exe` from the same source
pyinstaller --onefile --noconsole --name scatterplot_printer --add-data "config.json;." --add-data "file-list.json;." word_printer.py
```

- Output will be in `dist\scatterplot_printer.exe`.
- If your config or file-list are stored in `%APPDATA%\ScatterplotPrinter`, you don't need to bundle them, but bundling simplifies distribution.

5) Quick runtime checks (on the Windows machine)

- Test without printing by enabling `test_mode` in `config.json` (true), then run:

```powershell
.\dist\scatterplot_printer.exe
```

- If you prefer to run the script directly (no EXE), use:

```powershell
venv\Scripts\Activate.ps1
python word_printer.py
```

6) Distribution notes (for giving to other users)

- The simplest distributable is a ZIP containing:
  - `scatterplot_printer.exe` (from `dist`)
  - `config.json` (example edited for the recipient)
  - `file-list.json` (or instruct them to populate via Explorer)
  - `README.md` and `run_exe.bat` (optional)

- Users can place `config.json` and `file-list.json` next to the EXE or in `%APPDATA%\ScatterplotPrinter`.

7) Troubleshooting duplex enforcement

- Driver-level enforcement uses DEVMODE and is printer/driver specific. If the EXE cannot force duplex for a particular printer, the script will try Word-level settings but you may need a manual two-pass workaround. Test on a machine with the target printer.

Packaging the `tkinter` GUI (optional)

If you want to produce a separate GUI executable for non-technical users (`config_gui.exe`), build it with PyInstaller as a windowed app. Example commands:

```powershell
# Build the CLI/main printer EXE (console suppressed)
pyinstaller --onefile --noconsole --add-data "config.json;." --add-data "file-list.json;." --add-data "logs;logs" word_printer.py

# Build the GUI EXE (tkinter) as a windowed app
pyinstaller --onefile --windowed --add-data "config.json;." --add-data "file-list.json;." --add-data "logs;logs" config_gui.py
```

Notes and common PyInstaller flags

- `--onefile` creates a single bundled EXE. This is the simplest for distribution.
- `--noconsole` or `--windowed` prevents a console window from appearing for GUI users.
- `--add-data "source;dest"` bundles data files. On Windows use a semicolon (`;`) between source and dest.
- Common hidden imports when bundling pywin32 or other packages sometimes include `win32timezone`. If you see import errors, rebuild with:

```powershell
pyinstaller --onefile --noconsole --hidden-import=win32timezone --add-data "config.json;." --add-data "file-list.json;." word_printer.py
```

- If packaging both EXEs, include `config.json` and `file-list.json` (or instruct users to place them in `%APPDATA%\ScatterplotPrinter`).

Testing the GUI EXE

- After building `config_gui.exe`, run it to confirm it opens and can read/write `config.json` and `file-list.json` in the same folder.


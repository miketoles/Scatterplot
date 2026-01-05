# Building `scatterplot_printer.exe` (no-admin, minimal steps)

These steps build a one-file Windows EXE from `word_printer.py`. No admin rights needed if Python is installed per-user.

1) Install Python (one-time)
- Install Python 3.10 or 3.11 (Microsoft Store or user installer).
- Verify: `python --version`

2) Create a venv and install deps (one-time per machine)

```powershell
cd C:\path\to\word-variant
python -m venv venv
venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install pywin32 pyinstaller
```

3) Build the EXE

```powershell
pyinstaller --onefile --noconsole --name scatterplot_printer --add-data "config.json;." --add-data "file-list.json;." word_printer.py
```

Output: `dist\scatterplot_printer.exe`

4) Quick test

- Set `test_mode` to `true` in `config.json`.
- Run: `.\dist\scatterplot_printer.exe`

5) Share with others

Zip and send:
- `dist\scatterplot_printer.exe`
- `config.json`
- `file-list.json`
- `run_exe.bat` (optional)

Users can keep `config.json` and `file-list.json` next to the EXE or in `%APPDATA%\ScatterplotPrinter`.

Troubleshooting
- If you see missing module errors when running the EXE, rebuild with:

```powershell
pyinstaller --onefile --noconsole --hidden-import=win32timezone --add-data "config.json;." --add-data "file-list.json;." word_printer.py
```

- Duplex enforcement is driver-specific. Test on a machine with the target printer installed.

Optional: GUI EXE (for non-technical users)

```powershell
pyinstaller --onefile --windowed --add-data "config.json;." --add-data "file-list.json;." config_gui.py
```

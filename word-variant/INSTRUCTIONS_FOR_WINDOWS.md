Quick Windows setup (no-admin)

1) Copy `word-variant` to the Windows PC.

2) Open PowerShell:

```powershell
cd C:\path\to\word-variant
python --version
python -m venv venv
venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

3) Configure (recommended):

```powershell
python config_gui.py
```

- Add the Word files to process.
- Set `printer_name` exactly as shown in Windows Printers.
- Leave `test_mode` true for initial tests.

4) Test run (no printing):

```powershell
python word_printer.py
```

5) Build and share EXE (optional):

```powershell
pip install pyinstaller
pyinstaller --onefile --noconsole --name scatterplot_printer --add-data "config.json;." --add-data "file-list.json;." word_printer.py
```

Share these files:
- `dist\scatterplot_printer.exe`
- `config.json`
- `file-list.json`
- `run_exe.bat` (optional)

Notes:
- `config.json` and `file-list.json` can sit next to the EXE or in `%APPDATA%\ScatterplotPrinter`.
- For real printing, set `test_mode` to `false` and test on a machine with the target printer.

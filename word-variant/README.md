# Scatterplot Printer — Word variant (Windows setup & usage)

This README explains how to run and distribute the `word_printer.py` prototype and how to build a one-file EXE (`word_printer.exe`) for Windows users who do not have admin rights.

Where files belong
- Place `config.json` and `file-list.json` either next to the EXE/script or in `%APPDATA%\ScatterplotPrinter`.

Quick run (no build)

1. Transfer the `word-variant` folder to the Windows machine.
2. Install Python (per-user) or use the Microsoft Store version.
3. (Optional but recommended) Create a venv and install `pywin32`:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install pywin32
python word_printer.py
```

Build the EXE (single-file)

See `BUILD.md` for the full step-by-step. In short:

```powershell
pip install pyinstaller
pyinstaller --onefile --noconsole --add-data "config.json;." --add-data "file-list.json;." word_printer.py
.\dist\word_printer.exe
```

Safety: test mode

- Before printing to real printers, enable `test_mode` in `config.json` (true). The script will then open and modify documents but not send them to the printer; this lets you validate replacements and save behavior.

Where to put files for a user

- Preferred: send a ZIP containing `word_printer.exe`, `config.json`, `file-list.json`, and `run_exe.bat`. The user extracts and double-clicks `run_exe.bat`.
- Alternative: put `config.json` into `%APPDATA%\ScatterplotPrinter` — the EXE will discover it there.

Troubleshooting

- If the script fails to set the printer by name, run `printui /s /t2` or use Settings → Printers to confirm the exact device name; place that string into `config.json` under `printer_name`.
- If duplex isn't enforced, test on the same Windows machine with a simple Word print job and confirm the printer driver exposes duplex settings. If driver-level setting fails, the script will fall back to Word-level options; if both fail, perform a manual two-pass duplex.

Support and next steps

- To help a non-technical recipient, I can produce a small GUI to edit `config.json` and `file-list.json`, then bundle it with PyInstaller. Ask me to add it and I'll implement and include build steps.

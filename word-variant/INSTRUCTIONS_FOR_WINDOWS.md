Steps to transfer and test on Windows (copy this file and the entire `word-variant` folder to your Windows PC)

1) Transfer folder

- Copy the full `word-variant` folder to the Windows PC (USB, network share, or cloud sync).

2) Per-user Python + venv (no admin required)

Open PowerShell and run:

```powershell
cd C:\path\to\word-variant
python --version
python -m venv venv
venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

3) Use the GUI to prepare config and file list (optional, recommended)

From the same PowerShell with the venv activated:

```powershell
python config_gui.py
```

- Use "Add files" to collect the Word documents you intend to process. Save the file list.
- Set `printer_name` to the exact printer device name shown in Windows Settings → Printers & scanners.
- Keep `test_mode`=true while validating.

4) Quick script run (test mode)

```powershell
# ensure venv active
python word_printer.py
```

5) Build the EXE (optional for distribution)

```powershell
pip install pyinstaller
pyinstaller --onefile --noconsole --name scatterplot_printer --add-data "config.json;." --add-data "file-list.json;." word_printer.py
# result: dist\scatterplot_printer.exe
```

6) Run the EXE

- Place `config.json` and `file-list.json` next to `scatterplot_printer.exe` or in `%APPDATA%\ScatterplotPrinter`.
- Use `run_exe.bat` to launch.

7) Test duplex printing

- Set `test_mode` to `false` and run on a machine with the target printer installed.
- If duplex enforcement fails, try manually printing a small document from Word to confirm printer duplex option.

8) Distribute

- Zip the files in `distribution_manifest.txt` (except the EXE build output if you want to build on the target machine).

Contact me if you want a signed installer or an MSI — that will require additional packaging steps and optionally an admin to install.

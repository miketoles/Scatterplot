# Scatterplot Printer (Word)

Automatically updates dates in Word document headers and prints them to a configured printer.

## Installation (One-Click)

**Double-click `INSTALL.bat`** - that's it!

The installer will:
1. Check for Python (install it if missing via Windows Package Manager)
2. Set up dependencies automatically
3. Build the application
4. Create a desktop shortcut
5. Launch the app

After installation, use the **"Scatterplot Printer"** shortcut on your desktop.

## Requirements

- Windows 10 or 11
- Microsoft Word installed
- Internet connection (for first-time setup only)

## Configuration

Edit these files in the `dist` folder (next to the EXE):

**config.json** - Printer and behavior settings:
```json
{
  "printer_name": "Your Printer Name",
  "duplex": true,
  "test_mode": true,
  "save_after_print": true
}
```

**file-list.json** - List of Word documents to process:
```json
{
  "files": [
    "C:\\Path\\To\\Document1.docx",
    "C:\\Path\\To\\Document2.docx"
  ]
}
```

## Test Mode

**Important:** Keep `test_mode: true` in config.json until you've verified everything works correctly. In test mode:
- Documents open and dates are updated
- Documents are NOT printed
- Changes are NOT saved

Once verified, set `test_mode: false` for production use.

## Troubleshooting

### "Python not found"
If the automatic Python install fails:
1. Go to https://www.python.org/downloads/
2. Download Python 3.11+
3. Run installer - **CHECK "Add Python to PATH"**
4. Re-run `INSTALL.bat`

### Printer name not working
Run this in PowerShell to see exact printer names:
```powershell
Get-Printer | Select-Object Name
```
Copy the exact name into `config.json`.

### Logs
Check `dist\logs\word_printer.log` for detailed error messages.

## Files Overview

| File | Purpose |
|------|---------|
| `INSTALL.bat` | One-click installer - run this first |
| `dist\scatterplot_printer.exe` | The app (created after install) |
| `dist\config.json` | Printer/behavior settings |
| `dist\file-list.json` | Documents to process |
| `word_printer.py` | Source code (not needed after install) |

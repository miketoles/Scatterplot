# Scatterplot Printer

Automatically update dates and print Word documents in bulk.

## What It Does

1. Maintains a list of Word documents you want to print regularly
2. Updates the date in each document's header (e.g., "Date: January 10, 2026")
3. Prints all documents to your default printer (duplex, long-edge flip)
4. Saves the updated documents

## Installation (One-Click)

**Double-click `INSTALL.bat`** - that's it!

The installer will:
1. Check for Python (install it if missing)
2. Set up dependencies automatically
3. Build the application
4. Create a desktop shortcut
5. Launch the app

After installation, use the **"Scatterplot Printer"** shortcut on your desktop.

## Requirements

- Windows 10 or 11
- Microsoft Word installed
- Internet connection (for first-time setup only)

## How to Use

1. **Add Files**: Click "Add Files" to select Word documents
2. **Set Date**: Choose the date you want written to documents
3. **Test First**: Keep "Test Mode" checked to preview without printing
4. **Print**: Click "Print All Documents" to process everything

The app automatically:
- Sorts files by name
- Saves your file list between sessions
- Uses your default printer
- Prints duplex (both sides, flip on long edge)

## Test Mode

**Important:** Keep "Test Mode" checked until you've verified everything works:
- Documents open and dates are updated
- Documents are NOT printed
- Changes are NOT saved

Uncheck Test Mode when ready for actual printing.

## Troubleshooting

### "Python not found"
If automatic Python install fails:
1. Go to https://www.python.org/downloads/
2. Download Python 3.11+
3. Run installer - **CHECK "Add Python to PATH"**
4. Re-run `INSTALL.bat`

### Documents not updating
- Make sure documents have "Date:" in the header
- Supported formats: "Date: January 5, 2026" or "Date: 1/5/2026"

### Logs
Check `%APPDATA%\ScatterplotPrinter\logs\` for detailed logs.

## Files

| File | Purpose |
|------|---------|
| `INSTALL.bat` | One-click installer - run this first |
| `scatterplot_app.py` | Main GUI application |
| `word_printer.py` | Word automation engine |

# Scatterplot Printer — Design Document

## Overview

A Windows desktop application that automates the process of updating dates in Word document headers and printing them in bulk.

## User Workflow (Manual vs Automated)

### Manual Process (Before)
1. Navigate to network folder with patient documents
2. Open Word document
3. Edit date in header (e.g., "Date: January 10, 2026")
4. Print with duplex (both sides, flip on long edge)
5. Save document
6. Repeat for each document (10-20+ documents)

### Automated Process (After)
1. Open Scatterplot Printer app
2. Add documents to list (one-time setup, list is saved)
3. Select date to print
4. Select printer (or use default)
5. Click "Print All Documents"
6. All documents processed automatically

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    scatterplot_app.py                       │
│                     (GUI - tkinter)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │  File List  │  │   Printer   │  │  Print Button    │   │
│  │  (sorted)   │  │  Selector   │  │                  │   │
│  └─────────────┘  └─────────────┘  └──────────────────┘   │
│  ┌─────────────┐  ┌─────────────┐                         │
│  │ Date Picker │  │  Test Mode  │                         │
│  │ (Mon/Day/Yr)│  │  Checkbox   │                         │
│  └─────────────┘  └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    word_printer.py                          │
│                  (Word COM Automation)                      │
│                                                             │
│  For each document:                                         │
│  1. Open in Word (hidden)                                   │
│  2. Find "Date:" in header/footer/body                      │
│  3. Replace date with selected date                         │
│  4. Print (duplex, long-edge)                              │
│  5. Save (if Test Mode OFF) and close                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              %APPDATA%\ScatterplotPrinter\                  │
│                                                             │
│  config.json     - Settings (test_mode, printer, duplex)   │
│  file-list.json  - Saved document list                     │
│  logs/           - Runtime logs                             │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Simple GUI
- Dark theme matching modern Windows apps
- File list with add/remove buttons (sorted by filename)
- Printer dropdown (Default + all available printers)
- Date picker (Month, Day, Year dropdowns)
- Test mode toggle
- Single "Print All" button

### 2. Auto-Save File List
- No export/import needed
- File list persisted to `%APPDATA%\ScatterplotPrinter\file-list.json`
- Sorted alphabetically by filename
- Survives app restarts

### 3. Printer Selection
- Dropdown lists "Default Printer" + all available printers
- Selection is saved between sessions
- Uses Windows print spooler API to enumerate printers

### 4. Date Replacement
- Finds "Date:" patterns in headers, footers, and body
- Supports formats:
  - `Date: January 5, 2026`
  - `Date: 1/5/2026`
  - `Date: __January 5, 2026__` (underscored)
- Preserves document formatting

### 5. Print Settings
- Duplex: both sides, flip on long edge (DEVMODE.Duplex = 2)
- Synchronous printing (waits for each doc)

### 6. Test Mode
- **Checked (ON):** Print but DON'T save changes to documents
- **Unchecked (OFF):** Print AND save changes to documents
- Defaults to ON for safety on first install
- User's choice persists between sessions
- Clear confirmation dialog shows what will happen

## Confirmation Dialog

Before printing, user sees:
```
Ready to process 5 document(s).

Date: January 10, 2026
Printer: Default Printer

TEST MODE:
  • Documents WILL print
  • Changes will NOT be saved
```

Or in production mode:
```
PRODUCTION MODE:
  • Documents WILL print
  • Changes WILL be saved
```

## Date Pattern Matching

The `word_printer.py` uses regex to find and replace dates:

```
Pattern: Date: [optional underscores] [date] [optional underscores]

Examples matched:
- "Date: January 5, 2026"
- "Date:     January 5, 2026"  (multiple spaces)
- "Date: __January 5, 2026__"
- "Date: _1/5/2026_"
- "Date: 01/05/2026"
```

## Installation

### One-Click Install (`INSTALL.bat`)
1. Checks for Python, installs via winget if missing
2. Creates virtual environment
3. Installs pywin32 and pyinstaller
4. Builds single-file EXE
5. Creates desktop shortcut
6. Launches app

### Requirements
- Windows 10/11
- Microsoft Word (for COM automation)
- Internet (first install only)
- No admin rights needed

## File Structure

```
word-variant/
├── INSTALL.bat          # One-click installer - DOUBLE-CLICK THIS
├── README.md            # User documentation
├── DESIGN.md            # This file
├── scatterplot_app.py   # Main GUI application
├── word_printer.py      # Word automation engine
├── config.json          # Default config
├── file-list.json       # Default empty list
├── requirements.txt     # Python dependencies
└── dist/                # Built EXE (created after install)
    └── ScatterplotPrinter.exe
```

## Distribution

To distribute to a new machine:
1. Copy the entire `word-variant` folder to the target machine
2. Double-click `INSTALL.bat`
3. Wait for installation to complete
4. Use the desktop shortcut "Scatterplot Printer"

## Future Enhancements (Not in V1)

- [ ] Progress bar during processing
- [ ] Per-document status indicators
- [ ] Schedule/timer for automatic runs
- [ ] Network folder watching for new documents
- [ ] Remove Test Mode once confidence is established

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
4. Click "Print All Documents"
5. All documents processed automatically

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    scatterplot_app.py                       │
│                     (GUI - tkinter)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │  File List  │  │ Date Picker │  │  Print Button    │   │
│  │  (sorted)   │  │ (Mon/Day/Yr)│  │                  │   │
│  └─────────────┘  └─────────────┘  └──────────────────┘   │
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
│  5. Save and close                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              %APPDATA%\ScatterplotPrinter\                  │
│                                                             │
│  config.json     - Settings (test_mode, duplex)            │
│  file-list.json  - Saved document list                     │
│  logs/           - Runtime logs                             │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Simple GUI
- Dark theme matching modern Windows apps
- File list with add/remove buttons
- Date picker (Month, Day, Year dropdowns)
- Test mode toggle
- Single "Print All" button

### 2. Auto-Save File List
- No export/import needed
- File list persisted to `%APPDATA%\ScatterplotPrinter\file-list.json`
- Sorted alphabetically by filename
- Survives app restarts

### 3. Date Replacement
- Finds "Date:" patterns in headers, footers, and body
- Supports formats:
  - `Date: January 5, 2026`
  - `Date: 1/5/2026`
  - `Date: __January 5, 2026__` (underscored)
- Preserves document formatting

### 4. Print Settings
- Uses system default printer (no configuration needed)
- Duplex: both sides, flip on long edge (DEVMODE.Duplex = 2)
- Synchronous printing (waits for each doc)

### 5. Test Mode
- When enabled:
  - Opens documents and updates dates
  - Does NOT send to printer
  - Does NOT save changes
- Essential for verification before production use

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
├── INSTALL.bat          # One-click installer
├── README.md            # User documentation
├── DESIGN.md            # This file
├── scatterplot_app.py   # Main GUI application
├── word_printer.py      # Word automation engine
├── config.json          # Default config (copied to APPDATA)
├── file-list.json       # Default empty list
├── requirements.txt     # Python dependencies
└── dist/                # Built EXE (after install)
    └── ScatterplotPrinter.exe
```

## Future Enhancements (Not in V1)

- [ ] Progress bar during processing
- [ ] Per-document status indicators
- [ ] Printer selection dropdown
- [ ] Schedule/timer for automatic runs
- [ ] Network folder watching for new documents

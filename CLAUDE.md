# CLAUDE.md - ScatterplotCreator

---

## Project Overview

**Name:** NRT Scatterplot Creator
**Purpose:** Desktop app for BCBAs to manage patient behavior scatterplots - standardized 4-page tracking documents
**Status:** Active - Ready for stakeholder demo
**Path:** `~/dev/ScatterplotCreator`

---

## Quick Start

```bash
# Development
npm install
npm start

# Build Windows installer
npm run build

# Create deployment ZIP
# After build, ZIP is at dist/NRT-Scatterplot-Creator.zip
```

---

## Architecture

Electron app with a single-page UI. Main process handles file I/O and PDF generation. Renderer process is pure HTML/CSS/JS with no framework dependencies.

```
ScatterplotCreator/
├── main.js              # Electron main process, IPC handlers, PDF generation
├── index.html           # Complete UI (HTML + CSS + JS in one file)
├── pdf-template.html    # HTML template for PDF rendering (matches UI exactly)
├── preload.js           # Secure IPC bridge
├── install.bat          # Windows installation script
├── data-templates/      # Default JSON files copied on first run
└── dist/                # Build output
    └── win-unpacked/    # Portable Windows app
```

---

## Key Files

| File | Purpose |
|------|---------|
| `main.js` | ~550 lines - Electron main process, file I/O, PDF generation via `printToPDF` |
| `index.html` | ~1900 lines - Complete UI, all pages, CSS, and JS |
| `pdf-template.html` | ~450 lines - HTML template for PDF, uses same CSS as UI for pixel-perfect match |
| `DESIGN.md` | Comprehensive design document with all specs |

---

## Tech Stack

- **Runtime:** Electron 40
- **UI:** HTML5 + CSS3 + Vanilla JavaScript
- **PDF Generation:** Electron `printToPDF` (HTML-to-PDF)
- **Data Storage:** JSON files (network share compatible)
- **Build Tool:** electron-builder
- **Package Manager:** npm

---

## Current State

**What's working:**
- Patient list with sorting, CRUD operations
- Edit page with validation
- 4-page scatterplot preview (matches PDF exactly)
- PDF export (single patient or batch)
- Print All functionality
- Settings for data/PDF paths
- Concurrency handling for multi-user network deployment
- Back/Save button logic (unsaved changes detection)
- Cancel Changes functionality

**Recent fixes (Jan 26, 2026):**
- [x] Back button shows "Back" vs "Save and Go Back" based on unsaved changes
- [x] View Scatterplot uses date picker value
- [x] Consistent spacing around Add New Patient buttons

**Known issues:**
- None currently

---

## Development Notes

### PDF Generation
Uses Electron's `printToPDF` to render `pdf-template.html` with the same CSS as the UI preview. This guarantees pixel-perfect match between screen and print.

### Default Paths (Hospital Network)
- Data: `L:\BI Program Behavior Plans\Scatterplot Creator Data\data`
- PDF Export: `L:\BI Program Behavior Plans\Scatterplot Creator Data\pdf output`

### Deployment
1. Build with `npm run build`
2. ZIP the `dist/win-unpacked` folder (includes `install.bat`)
3. Users extract and run `install.bat` to install to `%LOCALAPPDATA%\Programs\`

### Important Functions
- `hasUnsavedChanges()` - Compares current patient to original for detecting edits
- `updateBackButton()` - Controls Back/Save button text and Cancel button visibility
- `generatePDFFromHTML()` - Creates PDF via hidden BrowserWindow + printToPDF

---

## Related Files

- `DESIGN.md` - Full design document with specs, data model, UI pages
- `FORMIKE.md` - Learning document (bugs, lessons, patterns)
- `STATUS.md` - Current status and next steps
- `DEPLOYMENT.md` - Windows installation guide

---

## Commands Reference

```bash
# Development
npm start                    # Run in dev mode

# Building
npm run build               # Build Windows (unpacked + installer)
npm run build:portable      # Build portable ZIP only
npm run build:installer     # Build NSIS installer only

# After building, create deployment ZIP:
cd dist && zip -r NRT-Scatterplot-Creator.zip win-unpacked
```

---

## For Mike (Learning Mode)

Key patterns in this project:
1. **HTML-to-PDF** - Using Electron's printToPDF for pixel-perfect PDF generation
2. **Optimistic Concurrency** - Timestamp-based conflict detection for multi-user
3. **State Management** - Comparing JSON snapshots to detect unsaved changes
4. **Single-file UI** - All HTML/CSS/JS in one file for simplicity

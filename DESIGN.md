# NRT Scatterplot Creator - Design Document

## Executive Summary (For Technical Stakeholders)

### What Is This App?

The NRT Scatterplot Creator is a desktop application designed for hospital behavioral health teams. It allows BCBAs (Board Certified Behavior Analysts) and clinical staff to manage patient behavior tracking sheets called "scatterplots" - standardized 4-page documents used to record patient behaviors in 15-minute intervals across a 24-hour period.

**The app solves a real workflow problem:** Previously, staff had to manually create these documents in Word or Excel, leading to inconsistent formatting, version confusion, and wasted time. This app provides a centralized patient list where behaviors are defined once, and staff can print fresh scatterplots daily with a single click.

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Runtime** | Electron 28+ | Cross-platform desktop app framework (Chromium + Node.js) |
| **UI** | HTML5 + CSS3 + Vanilla JavaScript | Single-page application, no framework dependencies |
| **PDF Generation** | Electron printToPDF | HTML-to-PDF conversion for pixel-perfect UI match |
| **Data Storage** | JSON files | Simple file-based storage, no database required |
| **Build Tool** | electron-builder | Creates Windows installer (.exe) |
| **Package Manager** | npm | Node.js dependency management |

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Electron Application                         │
├─────────────────────────────────────────────────────────────────┤
│  Renderer Process (index.html)                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ UI Layer: HTML/CSS/JavaScript                               ││
│  │ - Patient list management                                   ││
│  │ - Edit forms                                                ││
│  │ - Scatterplot preview (HTML rendering)                      ││
│  └─────────────────────────────────────────────────────────────┘│
│                            │ IPC (Inter-Process Communication)   │
│                            ▼                                     │
│  Main Process (main.js)                                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ - File I/O (read/write JSON)                                ││
│  │ - PDF generation (Electron printToPDF)                      ││
│  │ - System dialogs (file picker, confirmations)               ││
│  │ - Shell integration (open folders, print)                   ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  preload.js - Secure bridge exposing only necessary APIs        │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  File System (Network Share or Local)                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │patients.json │ │ doctors.json │ │  bcbas.json  │             │
│  │              │ │              │ │              │             │
│  │ Patient list │ │ Dropdown     │ │ Dropdown     │             │
│  │ + behaviors  │ │ options      │ │ options      │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Electron over Web App**: Chosen for easy file system access, native printing, and offline capability. No server infrastructure required.

2. **JSON over Database**: Simple, human-readable storage that can live on a network share. Easy to backup, inspect, and manually edit if needed.

3. **HTML-to-PDF via Electron**: Uses Electron's `printToPDF` to render the same HTML/CSS as the UI preview, guaranteeing pixel-perfect match between screen and print.

4. **Vanilla JS over React/Vue**: Minimizes dependencies, reduces build complexity, and keeps the app lightweight (~100MB installed).

5. **Optimistic Concurrency**: For multi-user scenarios, the app detects conflicts via timestamps rather than using file locking, avoiding the complexity of a real-time sync system.

### Dependencies

**Runtime Dependencies (bundled with app):**
- `electron` - Application framework (includes printToPDF for PDF generation)

**Build Dependencies:**
- `electron-builder` - Creates distributable installers

**System Requirements:**
- Windows 10/11 (primary target) or macOS 12+
- 100MB disk space
- Network share access (for multi-user deployment)
- No internet connection required after installation

### Installation Options

**Option A: Development/Testing (requires Node.js)**
```bash
# Install Node.js LTS first
git clone [repository]
cd ScatterplotCreator
npm install
npm start
```

**Option B: Production (standalone installer)**
```bash
npm run dist
# Creates: dist/NRT Scatterplot Creator Setup.exe
# Double-click to install like any Windows app
```

### Multi-User Network Deployment

1. Install app on each workstation
2. Create shared folder on network drive (e.g., `\\SERVER\ScatterplotData`)
3. Each user opens Settings and points Data Location to shared folder
4. All users now share the same patient list
5. Concurrency handling prevents data corruption from simultaneous edits

### Security Considerations

- **No PHI in app data**: Patient identifiers are room numbers + initials only (e.g., "301 JS")
- **Local/network storage only**: No cloud services or external APIs
- **No authentication**: Relies on Windows network permissions for access control
- **Electron security**: Context isolation enabled, Node integration disabled in renderer

### Maintenance

- **Adding doctors/BCBAs**: Edit `doctors.json` or `bcbas.json` in the data folder (no code changes needed)
- **Updating max behaviors**: Edit `config.json` in the data folder
- **Logs**: Check Electron DevTools console (Ctrl+Shift+I) for debugging
- **Data backup**: Simply copy the JSON files from the data folder

### Source Code Structure

```
main.js           # 550 lines  - Electron main process, IPC handlers, PDF generation
index.html        # 1600 lines - Complete UI (HTML + CSS + JS in one file)
pdf-template.html # 300 lines  - HTML template for PDF rendering (matches UI exactly)
preload.js        # 35 lines   - IPC bridge
```

Total: ~2,600 lines of code for a fully functional production application.

---

## Overview

A desktop application for BCBA teams to manage patient behavior lists and generate standardized, print-ready scatterplot PDFs. The system supports shared data across a small Microsoft network (under 12 users) with optimistic concurrency control.

**App Name:** NRT Scatterplot Creator
**Platform:** Windows (primary), macOS (development)
**Technology:** Electron (with HTML-to-PDF via printToPDF)
**Current Version:** January 2026

---

## Goals

- Easy, error-proof creation of scatterplots for each patient
- Consistent PDF output across all users
- Simple sharing of patient data across a small internal network
- Minimal training required for staff
- Batch printing of all scatterplots with a single click

---

## Users

- BCBAs (Board Certified Behavior Analysts)
- Observers / RBTs
- Clinical staff printing and filing reports

---

## Application Structure

### File Structure

```
ScatterplotCreator/
├── build/
│   └── icon.ico              # Windows app icon
├── data-templates/           # Template files copied on first run
│   ├── patients.json
│   ├── doctors.json
│   ├── bcbas.json
│   └── config.json
├── node_modules/             # Dependencies
├── pdf output/               # Default export location
├── DEPLOYMENT.md             # Windows installation guide
├── DESIGN.md                 # This file
├── electron-builder.yml      # Build configuration
├── index.html                # Main UI (single-page app)
├── main.js                   # Electron main process
├── package.json              # NPM configuration
├── pdf-template.html         # HTML template for PDF rendering
├── preload.js                # Electron preload script
└── scatterplot_bottom.png    # Instructions image for PDF
```

### Data Storage

**Location:** Configurable (default: `Documents/NRT Scatterplot Creator/`)

**Files:**
```
{dataRoot}/
├── patients.json       # Patient list with behaviors
├── doctors.json        # List of doctors for dropdown
├── bcbas.json          # List of BCBAs for dropdown
├── config.json         # App configuration (max behaviors, etc.)
└── pdf output/         # Default PDF export location (configurable separately)
```

---

## Data Model

### patients.json

```json
{
  "lastModified": "2026-01-24T15:30:00Z",
  "modifiedBy": "DOMAIN\\username",
  "patients": [
    {
      "id": "301-js-1706123456789",
      "displayId": "301 JS",
      "doctor": "Jones",
      "bcba": "Sally",
      "behaviors": [
        { "title": "Aggression", "description": "Hitting, kicking, biting..." },
        { "title": "Elopement", "description": "Leaving designated area..." }
      ],
      "createdAt": "2026-01-20T10:00:00Z",
      "updatedAt": "2026-01-24T15:30:00Z"
    }
  ]
}
```

### doctors.json / bcbas.json

```json
{
  "_instructions": [
    "This file contains the list of doctors/BCBAs available in the dropdown.",
    "To add: Add their name as a new line in the array below.",
    "To remove: Delete their line from the array."
  ],
  "doctors": ["Makley", "Jones", "Spier"]
}
```

### config.json

```json
{
  "_instructions": [
    "maxBehaviors: Maximum behaviors per patient (1-10).",
    "The scatterplot PDF layout is optimized for 4 behaviors."
  ],
  "maxBehaviors": 4
}
```

---

## UI Pages

### 1. Main Page (Patient List)

Clean, compact list of all patients with:
- Patient ID (Room# Initials format, e.g., "301 JS")
- Last updated date
- Doctor and BCBA
- Behavior summary (centered)
- Edit, View, Delete buttons (always visible)

**Header Actions:**
- Open PDFs Folder - Opens PDF export directory
- Print All Scatterplots - Opens batch print dialog
- Settings (gear icon) - Opens settings page

**Bottom:**
- Add New Patient button

### 2. Edit Page

Full-screen editor for a single patient:

**Header:**
- "Save and Go Back" button (validates and saves)
- Patient title
- View Scatterplot button
- Export PDF button

**Patient Information Section:**
- Patient ID input (format: Room# Initials)
- Doctor dropdown
- BCBA dropdown

**Behaviors Section:**
- Section header with "+ Add" button
- Each behavior shows:
  - Title input
  - Description textarea
  - Delete button
- Shows "X of Y behaviors" count

### 3. View Page

Scatterplot preview with print/export options:

**Header:**
- Back button (returns to previous page)
- Patient title
- Date picker (defaults to tomorrow)
- Print button
- Export PDF button

**Content:**
- Full 4-page scatterplot preview (scrollable)
- Starts at top of page when opened

### 4. Settings Page

**Data Location:**
- Current path display
- Browse button to change
- Open Folder button
- Note about editing doctors.json/bcbas.json

**PDF Export Location:**
- Separate configurable location
- Browse and Open Folder buttons

**Current User:**
- Shows logged-in username (domain\user when available)

### 5. Print All Modal

**Date Picker:**
- Defaults to tomorrow's date
- Light background for visibility

**Patient Selection:**
- Select All / Deselect All buttons
- Checkbox list of all patients with behavior summaries
- Cancel and Print Selected buttons

**Behavior:**
- Generates single combined PDF with all selected patients
- Opens PDF in default viewer for user to print with system dialog

---

## PDF Structure (4 Pages per Patient)

**Page 1:** 7:00 AM - 2:59 PM (32 rows, 15-minute intervals)
**Page 2:** 3:00 PM - 10:59 PM
**Page 3:** 11:00 PM - 6:59 AM
**Page 4:** Notes/Comments + Instructions

### Page Layout (Pages 1-3)

**Header:**
- Date, Doctor, Patient, BCBA
- Observer field (blank for handwriting)
- Shift indicator (Day/Evening/Night)

**Behavior List:**
- "Behaviors for data collection: 1.) Title 2.) Title..."

**Directions:**
- "Directions: Please shade in the box, if one or all behavior occurs in 15-minute increments."

**Grid:**
- Time column (12%)
- Checkmark column (4%)
- For each behavior (remaining width split evenly):
  - Data column (for shading)
  - Description column (gray background, full height)

**Footer:**
- "Please look at last page for instructions."

### Page 4 (Notes)

- Same header as other pages
- Notes grid: Shift / Observer / Notes (3 rows: Day, Evening, Night)
- Instructions box with example image

---

## Concurrency Handling

When multiple users share the same data folder:

1. On load: Cache `lastModified` timestamp
2. On save: Compare current file's `lastModified` to cached version
3. If unchanged: Save normally, update `lastModified` and `modifiedBy`
4. If changed: Show conflict notification, reload latest data

---

## Validation Rules

- **Patient ID:** Required, unique, format: `3 digits + space + 2-4 letters`
- **Doctor/BCBA:** Selected from dropdown (populated from JSON files)
- **Behaviors:** Minimum 1 required, maximum configurable (default 4)
- **Behavior Title:** Should be filled in (empty behaviors excluded from PDF)
- **Behavior Description:** Optional but recommended

---

## Key Features

### Print All Scatterplots
- Generates single combined PDF with all selected patients
- Each patient = 4 pages
- Opens in default PDF viewer for system print dialog
- User can choose printer and options

### Date Handling
- Default date is always tomorrow (system date + 1)
- Date picker uses light background for icon visibility
- Date displayed as "Month DD, YYYY" in PDF

### Auto-Save
- Changes saved automatically when navigating away from Edit page
- Validation required before saving

### Data Migration
- App automatically migrates old data format (raw array) to new format
- Old field names (e.g., "patient" → "displayId") handled transparently

---

## Installation (Windows)

See `DEPLOYMENT.md` for complete installation instructions.

**Quick Start:**
1. Install Node.js (LTS version)
2. Clone/copy project folder
3. Run `npm install`
4. Run `npm start` to launch
5. Configure data location in Settings to point to network share

**Building Installer:**
```bash
npm run dist
```
Creates `.exe` installer in `dist/` folder.

---

## Development

**Requirements:**
- Node.js 18+ (LTS)
- npm

**Commands:**
```bash
npm install    # Install dependencies
npm start      # Run in development mode
npm run dist   # Build Windows installer
```

**Key Files:**
- `main.js` - Electron main process, IPC handlers, file I/O
- `index.html` - All UI code (HTML + CSS + JavaScript)
- `pdf-template.html` - HTML template for PDF generation (uses same CSS as UI)
- `preload.js` - Secure bridge between renderer and main process

---

## Future Considerations

### Committee Redesign
A committee is designing an updated scatterplot format. Changes may include:
- Layout modifications
- New/changed fields
- Different behavior block format
- Updated instructions page

### Potential Enhancements
- Excel export for data analysis
- Search/filter patients
- Behavior templates library
- Print history/audit log
- Multiple scatterplot formats

---

## Technical Notes

### PDF/UI Parity
The PDF generator uses Electron's `printToPDF` to render the same HTML/CSS template as the UI preview. This ensures:
- Pixel-perfect match between UI preview and printed PDF
- Same fonts, colors, spacing, and layout
- No manual positioning or style synchronization needed

### Form Styling
All form inputs use light backgrounds (#fff) for visibility with dark theme, especially important for:
- Date picker calendar icon
- Dropdown arrows
- Text contrast

### Electron Security
- Context isolation enabled
- Node integration disabled in renderer
- All file/system operations go through IPC handlers in main.js
- preload.js exposes only necessary API methods

---

*Last updated: January 25, 2026*

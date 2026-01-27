# FORMIKE.md - ScatterplotCreator: The Full Story

---

## What This Project Actually Does

Imagine you're a BCBA (Board Certified Behavior Analyst) at a hospital. Every day, you need to create these 4-page documents called "scatterplots" for each patient. They're basically grids where staff mark when certain behaviors happen throughout the day - 15-minute intervals, 24 hours.

Before this app, people were creating these in Word or Excel. Chaos. Different formatting, version confusion, wasted time. This app gives them a simple patient list where they define behaviors once, then print fresh scatterplots daily with one click.

---

## The Architecture (How It All Fits Together)

Think of it like a restaurant with a kitchen and a dining room:

```
┌─────────────────────────────────────────────────────────────┐
│                     The Restaurant                           │
├─────────────────────────────────────────────────────────────┤
│  Dining Room (Renderer Process - index.html)                │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ What customers see and interact with                    ││
│  │ - Patient list (the menu)                               ││
│  │ - Edit forms (ordering)                                 ││
│  │ - Preview (seeing the dish before it's served)          ││
│  └─────────────────────────────────────────────────────────┘│
│                    │                                         │
│              The Pass (IPC)                                  │
│         Orders go to kitchen, food comes back                │
│                    │                                         │
│  Kitchen (Main Process - main.js)                           │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Where the real work happens (customers don't see)       ││
│  │ - Reading/writing JSON files (pantry)                   ││
│  │ - Generating PDFs (cooking)                             ││
│  │ - Opening file dialogs (supplier orders)                ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
        Network Share (walk-in cooler)
        └── patients.json, doctors.json, etc.
```

### The Key Players

**index.html** - The entire front-end in one file
- Think of it like: A self-contained restaurant with all the furniture, decorations, and menus built-in
- Contains: HTML structure + CSS styling + JavaScript logic
- Why one file? Simplicity. No build step, no framework complexity. Just open and it works.

**main.js** - The Electron main process
- Think of it like: The kitchen staff
- Handles: File operations, PDF generation, system dialogs
- Security: Runs with Node.js powers that the browser can't have

**pdf-template.html** - The PDF rendering template
- Think of it like: A mold for making identical dishes
- Uses the same CSS as the UI, so what you see is what you get
- Gets injected with patient data, then converted to PDF

---

## The Codebase: A Guided Tour

```
ScatterplotCreator/
├── main.js              → The brain - handles files, PDFs, system stuff
├── index.html           → The face - everything the user sees and clicks
├── pdf-template.html    → The printer - HTML that becomes the PDF
├── preload.js           → The translator - secure bridge between brain and face
├── install.bat          → The setup wizard - Windows installation script
├── DESIGN.md            → The blueprint - all the specs and decisions
├── data-templates/      → The starter kit - default JSON files
└── dist/                → The delivery box - built app ready to ship
```

### The Most Important Files

**index.html** (~1900 lines) - This is where the magic happens for users. It's a single-page app with multiple "pages" that show/hide. The state management is simple: one `state` object holds everything.

**main.js** (~550 lines) - This handles the "privileged" operations. The key insight: browsers can't read/write arbitrary files (security!), but Electron's main process can. So we define IPC handlers that the renderer can call.

**pdf-template.html** - The trick that made everything click. Instead of using PDFKit to manually position every element (nightmare!), we render HTML and let Chromium convert it to PDF. Same CSS = pixel-perfect match.

---

## Tech Decisions: Why We Built It This Way

### Why Electron over a Web App?

**The decision:** Desktop app instead of web app.

**Why:**
- Need to read/write files on local machine and network share
- Need native printing and PDF generation
- Must work offline
- No server infrastructure to maintain
- Hospital IT doesn't want to manage a web server

**What I learned:** Electron is perfect for "enhanced browser" use cases. It's overkill for simple apps, but when you need file system access + web tech, it's the answer.

### Why HTML-to-PDF instead of PDFKit?

**The decision:** Switched from PDFKit (manual coordinate positioning) to Electron's `printToPDF`.

**Why:** PDFKit was a nightmare. You have to manually position every single element with x/y coordinates. When the UI changed, the PDF didn't match. With HTML-to-PDF, we use the same CSS for both, so they're always in sync.

**What I learned:** Don't fight the platform. HTML/CSS is designed for layout. Use it.

### Why Vanilla JS instead of React?

**The decision:** Plain JavaScript, no framework.

**Why:**
- ~2000 lines of code total - frameworks add complexity without benefit at this scale
- No build step means simpler deployment
- Hospital staff don't need hot reloading or fancy dev tools
- One less thing to break or update

**What I learned:** Frameworks solve real problems, but only use them when you have those problems. Small apps don't need React.

---

## The Journey: Bugs, Fixes, and "Aha!" Moments

### Bug #1: Empty ZIP File

**What happened:** After running `npm run build:portable`, the ZIP file was 0 bytes.

**What I tried:** Checked electron-builder config, rebuilt multiple times.

**The fix:** The electron-builder portable target was broken. Instead, we manually ZIP the `win-unpacked` folder after a regular build.

**The lesson:** Build tools have bugs. When something doesn't work, check if you can do it manually first.

---

### Bug #2: GPU Process Crash on Network Share

**What happened:** App crashed with "GPU process launch failed" when run directly from network share.

**What I tried:** Various Electron flags, different run methods.

**The fix:** Electron (Chromium) can't run properly from a network path. Solution: Install locally to `%LOCALAPPDATA%`, but data files can still live on network share.

**The lesson:** Chromium has quirks. Some things just won't work in certain environments. Find a workaround.

---

### Bug #3: PDF Didn't Match UI

**What happened:** Used PDFKit to generate PDFs. Manual positioning meant constant drift between UI preview and printed PDF.

**What I tried:** Endless tweaking of coordinates, checking measurements.

**The fix:** Abandoned PDFKit entirely. Created `pdf-template.html` with same CSS as UI. Use Electron's `printToPDF` to render HTML to PDF.

**The lesson:** If you're fighting the tool, you might be using the wrong tool. HTML-to-PDF is the right approach for web-based layouts.

---

### Bug #4: Back Button Logic Wrong

**What happened:** Back button showed "Save and Go Back" based on whether patient was empty, not whether there were unsaved changes.

**What I tried:** N/A - this was a design flaw from the start.

**The fix:** Created `hasUnsavedChanges()` function that compares current patient JSON to original snapshot. Button text and Cancel button visibility based on this.

**The lesson:** State management matters. Comparing JSON snapshots is a simple way to detect changes without tracking every field.

---

### Bug #5: Grey Backgrounds Not Printing

**What happened:** PDF previews showed grey backgrounds correctly, but printed pages came out white. Using "Print as Image" in Adobe didn't help either.

**What I tried:**
- Checked printer settings for "skip background graphics" (couldn't find it)
- Tried Adobe "Print as Image" option
- Verified the grey was in the PDF file

**The fix:** The grey (#f2f2f2) was too light - the Xerox Altalink B8155 printer was skipping it. Darkened to #e0e0e0 and it prints perfectly.

**The lesson:** Printers have a color threshold. Very light colors (especially greys) may be skipped entirely. When designing for print, test with actual hardware and use colors with enough contrast.

---

### Bug #6: Print All PDFs Not Sorted

**What happened:** When printing multiple patients with "Print All Scatterplots", the PDF output was in random order instead of sorted by patient ID.

**The fix:** Added `.sort((a, b) => a.displayId.localeCompare(b.displayId))` to the selected patients array before generating the PDF.

**The lesson:** Always consider output ordering for batch operations. Users expect sorted output.

---

## Patterns & Best Practices I Learned

### Pattern: Snapshot Comparison for Change Detection

**What it is:** Store a deep copy of data when editing starts. Compare current state to snapshot to detect changes.

**How we used it:**
```javascript
// When opening edit page
state.originalPatientData = JSON.parse(JSON.stringify(patient));

// To check for changes
function hasUnsavedChanges() {
  return JSON.stringify(state.editingPatient) !== JSON.stringify(state.originalPatientData);
}
```

**Where else I can use this:** Any edit form, undo/redo systems, conflict detection.

---

### Pattern: HTML-to-PDF for Pixel-Perfect Output

**What it is:** Instead of programmatically building PDFs, render HTML and convert to PDF.

**Why it's useful:** Layout stays in sync automatically. CSS is easier than coordinate math.

**How we used it:** Hidden BrowserWindow loads template, injects data, calls `printToPDF`.

---

## How Good Engineers Think

Things I observed from this project:

1. **Start simple, add complexity only when needed** - We started with vanilla JS and JSON files. No database, no framework. It works perfectly for 12 users.

2. **Match the tool to the problem** - Web tech for UI, Electron for file access, HTML-to-PDF for printing. Each tool does what it's good at.

3. **When something is hard, question the approach** - PDFKit was a constant fight. The moment we switched to HTML-to-PDF, everything got easier.

---

## Pitfalls to Avoid Next Time

**Don't run Electron apps from network shares** - Chromium's GPU process fails. Always install locally.

**Don't manually position PDF elements** - Use HTML-to-PDF instead. It's not just easier, it's more maintainable.

**Don't over-engineer for 12 users** - JSON files on a network share work fine. No need for a database.

---

## New Technologies I Learned

### Electron's printToPDF

**What it is:** A method that converts a BrowserWindow's contents to a PDF buffer.

**Why it exists:** Web pages need to become printable documents.

**The basics:**
```javascript
const pdfData = await win.webContents.printToPDF({
  landscape: true,
  pageSize: 'Letter',
  printBackground: true
});
fs.writeFileSync('output.pdf', pdfData);
```

---

## If I Built This Again...

1. **Start with HTML-to-PDF from day one** - Would have saved hours of PDFKit pain
2. **Create install.bat earlier** - Manual file copying was error-prone
3. **Add snapshot comparison immediately** - Would have avoided the Back button bug

---

## Key Takeaways (The TL;DR)

1. **Electron is great for "browser + file system" apps** - Simple to build, easy to deploy
2. **HTML-to-PDF beats programmatic PDF generation** - Same CSS, no coordinate math
3. **JSON files work fine for small user counts** - Don't over-engineer data storage
4. **Snapshot comparison is a simple way to detect changes** - Just compare JSON strings

---

*Last updated: January 26, 2026*
*Written by Claude Code as a learning companion for Mike*

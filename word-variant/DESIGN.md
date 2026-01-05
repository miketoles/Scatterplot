# Scatterplot Printer — Word Variant

## Current (browser) features

- UI: dark-themed single-file HTML app (`scatterplot-printer-word.html`).
- Select multiple Word files (`.doc`, `.docx`) via file picker.
- Persist selected file list in `localStorage` so selections survive page reloads.
- Export/import file lists as `scatterplot-file-list.json` for portability.
- Test Mode toggle: when enabled the instructions tell users not to save changes.
- Generate plain-text instruction file and copy to clipboard or download.

## Small changes made (this commit)

- Button text changed to **Add Scatterplot Files** to match product naming.
- Added Export (download JSON) and Import (upload JSON) buttons to move lists between machines.
- Implemented `scatterplot_files_v2_word` localStorage key to remember file metadata (name, path, size, lastModified). Note: browsers cannot persist File objects themselves — only metadata is stored.

## Goal: Windows Executable (fully automated)

Objective: produce a self-contained Windows executable that iterates through a user-configurable list of Word documents, updates the header date, prints to a configured network printer (duplex), optionally saves the document (unless Test Mode), and closes Word. The executable should remember printer settings and file list configuration per-user.

Repo: https://github.com/miketoles/Scatterplot.git

Constraints & Requirements:

- Target machines: Windows 10/11 with Microsoft Word installed (required for COM automation).
- No administrative privileges required for running the packaged EXE. Building the EXE is ideally done on a Windows build machine; cross-compilation from macOS is possible but brittle.
- Printer access: executable will call Word's print APIs and supply a printer name; network printer driver must be available on the target machine.

Recommended Implementation (Python / pywin32):

1. Core script: `word_printer.py` (to be added)
   - Uses `win32com.client.Dispatch('Word.Application')` to open documents, manipulate headers, call `PrintOut` with `ActivePrinter` set, set `Item`/`Copies`/`PrintToFile` options as needed.
   - Header/date update strategy: find header text occurrences of `Date:` or `Date` and replace the date substring. (Use a small regex or simple text search.)
   - Save behavior: if Test Mode is false, call `doc.Save()`; otherwise `doc.Close(SaveChanges=False)`.
   - Duplex/2-sided printing: set `Word.Application.ActivePrinter` to the configured printer name and set `doc.PrintOut(Background=False)`; duplex settings are often driver-specific — attempt to set `doc.PageSetup.Draft` or use DEVMODE via win32 API if needed.
   - Config: read `config.json` sitting next to the EXE (contains printer name, duplex boolean, file-list path, testMode boolean).

2. Packaging: `PyInstaller --onefile word_printer.py` on Windows.
   - Include `config.json` and optionally sample file-list. Use `--add-data` if necessary.
   - Resulting single EXE can be distributed to users; no admin install needed.

3. File list & settings storage:
   - Use `file-list.json` (full paths) stored in the same folder as the EXE or in `%APPDATA%/ScatterplotPrinter/` for per-user persistence.
   - `config.json` contains default printer, duplex, and save behavior.
   - The executable will locate `config.json` and `file-list.json` automatically so the user can run the EXE from any folder. Search order for each file:
     1. Explicit `--config` or `--files` argument passed to the EXE/script.
     2. Current working directory.
     3. Directory where the EXE/script lives.
     4. `%APPDATA%/ScatterplotPrinter/` (per-user storage).
   - Relative paths inside `file-list.json` are resolved relative to the `file-list.json`'s location so lists are portable.

4. UI for non-technical users:
   - Provide a simple GUI wrapper using `tkinter` (bundled with Python) to allow people to add/remove files, choose a printer from installed printers, toggle duplex, and run. Bundle GUI with the same PyInstaller build.
   - Alternatively, use the HTML file as the configuration UI and export `scatterplot-file-list.json` which users place next to the EXE.

5. Security & safety:
   - The EXE will run Word on behalf of the user; ensure it is run from trusted locations.
   - Test Mode exists to avoid saving changes while verifying behavior.

6. Build notes and commands (on Windows machine):

   - Create a virtualenv, install dependencies:

   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install pywin32 pyinstaller
   ```

   - Test the `word_printer.py` script on a dev Windows machine with Word installed.

   - Build single-file EXE:

   ```powershell
   pyinstaller --onefile --noconsole word_printer.py
   ```

   - Distribute the generated `dist\scatterplot_printer.exe` along with `config.json` or instruct users to create it via the HTML UI export.

## Completed work (so far)

- Browser UI: `scatterplot-printer-word.html` — dark theme, select `.doc/.docx`, per-file status, locate/re-link, export/import JSON.
- Settings UI: `printerName`, `duplex`, `testMode`, `autoExport`, persisted to `localStorage`.
- File persistence: `localStorage` + optional File System Access API support with IndexedDB-persisted handle to write `file-list.json` in-place (Chromium/Edge only); graceful fallback to download/upload.
- Export/import: JSON export (`scatterplot-file-list.json`) and import handled in the UI; example `file-list.json` and `config.json` added for Windows testing.
- Python prototype: `word_printer.py` included — opens Word via COM, replaces dates in headers/footers/body/fields/content-controls, prints, saves/closes. Prototype checks `%APPDATA%/ScatterplotPrinter/file-list.json` and searches multiple locations so the EXE can run from any folder.
- DESIGN.md updated to document storage and run-from-anywhere behavior.
 - Logging: `word_printer.py` now captures stdout/stderr to `logs/word_printer.log` next to the script/EXE for diagnostics.
 - GUI: `config_gui.py` (minimal `tkinter` helper) added to edit `config.json` and `file-list.json` for non-technical users; can be bundled via PyInstaller as a windowed app.
 - Distribution preview: created `word-variant-for-windows.zip` containing all necessary files (except the built EXE) to transfer to a Windows machine for testing.
 - Git: repository initialized and current changes committed; all added files have been staged and committed in the `Scatterplot Printer App` repo.

## Remaining work / Next steps (pickable items)

1. Test flows (high priority)
   - Validate File System Access flow on Chromium/Edge (choose handle, add files, ensure `file-list.json` updates in place).
   - Run `word_printer.py` on a Windows dev machine with Word installed using the example `config.json` and `file-list.json`.
   - Verify per-file re-link (`Locate`) and missing-file UI flows.

2. Duplex/printer reliability (recommended)
   - Implement DEVMODE-based duplex control in the prototype so duplex is enforced via printer driver (Windows-specific). This requires calling Win32 APIs and marshalling DEVMODE; will add as an optional module.
    - Note: a DEVMODE-based attempt has been added to the prototype (`word_printer.py`) to set `devmode.Duplex` where available, but this requires on-device testing with the target printer drivers. Marked as in-progress and requires verification/fallbacks.

3. User-facing configuration GUI (optional)
   - Create a small `tkinter` GUI for Windows to edit `config.json` and `file-list.json` and to test-print a single document. This GUI will be bundled with the EXE.

4. Packaging & distribution
   - Create `BUILD.md` and a reproducible PyInstaller spec to produce a single-file EXE. Build must be performed on Windows. Include signing and installer suggestions if required by your org.

5. Automation & safety
   - Add logging, detailed error handling for per-file failures, and a dry-run mode that lists intended changes without modifying files.
   - Add a verification step after saving: reopen the document and confirm the replacement occurred (non-destructive check in Test Mode)

6. Optional: Web → Desktop integration
   - Add a simple helper (CLI or small script) that copies `file-list.json` from the browser-chosen location into `%APPDATA%/ScatterplotPrinter/` on the Windows machine to bridge web UI and EXE usage for non-Chromium browsers.

   Recent commits & artifacts

   - `word-variant` now contains: `word_printer.py`, `config.json`, `file-list.json`, `config_gui.py`, `README.md`, `BUILD.md`, `INSTRUCTIONS_FOR_WINDOWS.md`, `requirements.txt`, `run_exe.bat`, `distribution_manifest.txt`, and the preview zip `word-variant-for-windows.zip` (placed in the parent folder).
   - A git repository was initialized in `Scatterplot Printer App` and changes committed. Use git to inspect history or revert if needed.

## How I'll proceed when you return

- If you ask me to continue, I will prioritize:
  1. Implementing DEVMODE duplex enforcement in `word_printer.py` (so printing is reliable across drivers).
  2. Adding `BUILD.md` with exact PyInstaller commands and a small `tkinter` config GUI prototype.
  3. Helping you test the flows and iterate on edge-case replacements for your provided reference files.

If you'd prefer a different order, tell me which items to prioritize and I'll pick them up next.

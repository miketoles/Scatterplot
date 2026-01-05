# Scatterplot Import — Design Document

Project: Scatterplot Import
Objective: reliably convert scanned daily scatterplot sheets (CNA-filled) into auditable entries in CentralReach (CR) with a human-in-the-loop verification workflow and explicit handling for edge cases.

Overview
- CNAs fill a paper scatterplot for each patient each day (7:00am → 6:59am next day) in 15‑minute intervals.
- Each row lists one behavior (typically 1–4). For each interval the cell is one of:
  - Blank / skipped
  - Checkmark / stroke (ERR)
  - Shaded / filled (IND)
  - Other: crossed-out blanks (X-through), diagonal multi-line Xs, heavy scribbles, or handwritten notes
- Input will commonly be one multi-page PDF (one page per patient/day). Each page must be processed independently and produce per-page outputs.

High-level requirements
- Accuracy: data written to CR must match the paper with negligible silent errors.
- Speed: support batch import of multi-page PDFs for clinic throughput.
- Usability: reviewers correct ambiguous or exceptional detections quickly.
- Security & compliance: keep PHI local when possible, encrypt sensitive files, and store audit logs.

Design summary — pipeline stages (updated)
1. Ingest: accept single- or multi-page PDFs, PNG/JPEG; watch a folder or accept drag/drop of files.
2. PDF → image(s): render each PDF page to an image (configurable DPI, 200–300 recommended).
3. Preprocess: convert to grayscale, denoise, deskew, and do perspective correction.
4. Template alignment: detect template variant or fiducials and warp page into canonical template coordinates.
5. Grid/cell extraction: compute deterministic cell boxes from template or fallback to grid detection.
6. Per-cell mark analysis: compute fill ratios, stroke/skeleton features, connected components, and run an ML classifier when available.
7. Exception detection (X-through, multi-line crosses, scribbles): special heuristics to recognize crossed-out rows and generate an "exception code".
8. Metadata OCR/HTR: extract patient, date, initials, and observer; prefer QR/barcode when present.
9. Candidate mapping: resolve behavior names to CR behavior IDs using API + local mapping.
10. Human review UI: surface ambiguous cells and exceptions with thumbnails and suggested labels.
11. Commit: batch-write verified data to CR (API preferred) and archive inputs with audit logs.

Multi-page PDFs and per-page metadata
- The system renders each PDF page and treats it as an independent document. Output CSV/JSON includes a `page` column and per-page metadata (detected date, patient id/room).

Mark & exception handling (new)
Overview:
- In real-world scans a cell may be marked in many ways: single checkmarks, shaded fills, an `X` drawn across blank rows, multiple parallel hatching lines, or scribbles. We must map these to canonical codes (ERR, IND, Blank) while capturing "weird" cases as exceptions for reviewer attention.

Rules and detectors:
- Standard detections (fast path):
  - Shaded / IND: high fill fraction (configurable, e.g., > 25–35%).
  - Checkmark / ERR: stroke-like connected component(s) with low fill fraction but high skeleton length relative to area.
  - Blank / Skip: low fill fraction and no stroke-like CC.
- X-through / crossed-out rows:
  - Detect long diagonal strokes crossing multiple cells within the same row band using Hough line detection and skeletonization.
  - If an X-line passes across > 50% of the row width and stroke thickness consistent with pen, mark as EX_X (exception: crossed-out).
  - If X-line passes through multiple adjacent rows, generate EX_MULTIROW_X and treat as reviewer-only by default.
- Multiple-line hatching (parallel short strokes across a whole column/cell):
  - High density of short parallel strokes increases fill fraction but has high orientation variance; mark as probable SHADING but add EX_HATCH flag when orientation variance or line-count thresholds exceed tuned values.
- Scribbles / heavy pen marks:
  - Very high fill fraction with irregular connected components flagged EX_SCRIBBLE; treat as IND candidate but push to reviewer.

Exception mapping (error taxonomy)
- Each detected unusual pattern is emitted as an exception code alongside the candidate label. Example exception codes:
  - EX_X: crossed-out row (X through blank)
  - EX_MULTIROW_X: X spanning multiple rows
  - EX_HATCH: hatching / multiple short lines
  - EX_SCRIBBLE: heavy scribble or overwritten cell
  - EX_OVERWRITE: handwritten change to a printed timestamp or field
  - EX_AMBIG: model confidence below threshold
- The UI shows exception code(s) for the row/cell and suggests a mapping rule. Reviewers can accept the suggested canonical label (ERR/IND/Blank) or pick a special action (mark ignored, map to ERR/IND, or enter free-text note).

Policy for automated mapping vs reviewer escalation
- Auto-commit only when:
  - No exceptions on the page AND
  - All cells have classifier confidence above `auto_accept_threshold` (configurable), AND
  - Behavior mapping to CR is exact or high-confidence.
- Otherwise, route document to quick review with highlighted exceptions.

Template & deterministic grid support
- For stable forms, store a `grid.json` per template with exact cell bounding boxes (x,y,w,h) in template coordinates. This deterministic approach is recommended when form variants are limited and yields much higher reliability than projection heuristics.
- `grid.json` also encodes meta rows (e.g., header rows, timestamp cells) and a few example patches for each cell to help per-site tuning.

ML and heuristics ensemble
- Use a lightweight CNN (e.g., MobileNet) as a second opinion on each cell patch. Combine outputs with heuristics (fill ratio, stroke/skel features) via a small ensemble (weighted voting) and produce a final label with confidence and a list of exception codes.

Human-in-the-loop UI (reviewer ergonomics)
- Show full page and a compact grid of thumbnails with labels, confidences, and exception badges. Keyboard shortcuts: accept all, accept page, toggle cell label (0/1/2), open patch in larger view, add free-text note.
- Bulk actions: apply same correction to a contiguous run (useful for X-through or multi-interval fills).

Output and audit
- Output each processed page as:
  - `results.csv` / `results.json` with `page,row,col,label,fill_fraction,confidence,exceptions` and extracted metadata (patient, date, source-file).
  - An audit bundle containing original PDF page image, warped image, per-cell patches for any exceptions, and reviewer decisions.

Integration with CentralReach (unchanged)
- Prefer API-based writes with secure credentials; fallback to browser automation only if API access not possible.

Testing & acceptance (updated)
- Create an annotated corpus covering: clean checks, faint shading, X-through blanks, diagonal Xs, multi-line hatch, scribbles, and handwriting overlap. Include multi-page PDFs mixing patients and dates.
- Acceptance: >99% auto-accept rate on clean pages; ambiguous & exception pages should be easily resolved by reviewer (median review time < 12s/page).

Next steps — prioritized
1. Add `grid.json` for canonical template(s) used at the clinic and implement deterministic per-cell extraction.
2. Run the CLI prototype on sample multi-page PDFs and produce debug overlays so we can tune thresholds (I can run this if you provide a sample PDF).
3. Implement exception detectors (X-through, hatch, scribble) and emit exception codes for review.
4. Build the reviewer UI and wire in the CR mapping step.

Appendix: quick heuristics summary
- Fill ratio thresholds: default IND > 0.25, suspect 0.12–0.25
- Stroke heuristic: skeleton_length / area ratio high → checkmark
- X-through detection: Hough lines crossing row band → EX_X
- Config: all thresholds adjustable per-site and stored with `template` metadata.

Contact & ownership
- Project owner: you (project lead)

Current implementation & how to run (snapshot)

- Repository path: `scatterplot-import/` (relative to project root).
- Prototype files added:
  - `requirements.txt` — dependencies (`opencv-python-headless`, `numpy`, `scipy`, `Pillow`, `PyMuPDF`).
  - `cli.py` — CLI entrypoint; supports single images and multi-page PDFs. Produces a combined CSV with a `page` column and optional per-page debug images.
  - `template_align.py` — simple page-contour detection and perspective warp to a canonical template size.
  - `mark_detector.py` — projection-profile-based column/row detection and per-cell fill-fraction + simple classification.
  - `README_PROTOTYPE.md` — quick-run instructions and examples.

How to run the prototype (recommended quick test):

```bash
cd scatterplot-import
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Single image
python cli.py /path/to/scan.png --debug --out results.csv --out-dir ./debug_outputs

# Multi-page PDF
python cli.py /path/to/scans.pdf --debug --out results.csv --out-dir ./debug_outputs
```

Outputs:
- `results.csv` — rows with `page,row,col,filled,fill_fraction` and per-page metadata where available.
- Debug images: for each page when `--debug` is used, `*_page{N}_warped.png` and `*_page{N}_debug.png` are written to `--out-dir`.

Implementation notes and current gaps:
- The CLI supports multi-page PDFs via `PyMuPDF` and renders pages at ~200 DPI by default in the prototype.
- The current `mark_detector.py` uses projection heuristics; it does not yet implement the full exception detectors (X-through, hatch, scribble). Those exception detectors are specified in the design and are the next implementation step.
- `grid.json` deterministic templates are not yet present — adding `grid.json` for your clinic's canonical form will drastically improve reliability and is recommended before large-scale runs.
- The prototype writes CSV/debug outputs locally; CR integration, reviewer UI, and active learning are not implemented yet and are scoped in the design.

Recommended immediate actions before production runs:
1. Provide one or two representative multi-page PDFs (scanned at 200–300 DPI) so I can run the prototype and produce debug overlays for tuning thresholds.
2. If forms are stable, create a `grid.json` describing precise cell boxes for the template; I can add a loader so the prototype will use deterministic cell extraction instead of projections.
3. Implement exception detectors (X-through/hatch/scribble) in `mark_detector.py` and emit `exceptions` codes in the CSV/JSON output.

If you'd like, I can now (pick one):
- Run the CLI on your uploaded PDF(s) and return `results.csv` + debug images, or
- Add a `grid.json` schema and example for the current template, or
- Implement the exception detectors as code and wire them to the CLI outputs.

Status log (session handoff)
- Sample PDF provided at `scatterplot-import/Scanned from a Xerox Multifunction Printer.pdf` (single patient, should still validate multi-page handling).
- Attempted to run `cli.py` but missing `cv2` (deps not installed). Need `pip install -r requirements.txt` in a venv (network access required).
- CR API docs not found publicly; likely gated behind CentralReach community/support. Next step is to request API docs/credentials from CentralReach.
- Temporary `bing.html` file from web search was deleted.
- Awaiting approval to install deps, run CLI on the sample PDF, and generate debug overlays + `results.csv`.

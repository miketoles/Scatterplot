# Prototype README — Scatterplot Import CLI

This prototype provides a minimal CLI to align a scanned scatterplot sheet to a template and detect filled cells.

Files:
- `cli.py` — entrypoint. Usage: `python cli.py scan.png --debug`
- `template_align.py` — warps the scanned page by detecting its largest contour.
- `mark_detector.py` — detects columns/rows via projection profiles and returns per-cell fill fractions.
- `requirements.txt` — Python dependencies.

Quick start

1. Create a venv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the prototype on an image or PDF:

```bash
# Single image
python cli.py /path/to/scan.png --debug --out results.csv

# Multi-page PDF (writes combined CSV with `page` column, and per-page debug images when --debug)
python cli.py /path/to/scans.pdf --debug --out results.csv --out-dir ./debug_outputs
```

3. Output:
- `results.csv` — rows with `row,col,filled,fill_fraction`.
- Debug images written next to the input image when `--debug` is used.

Next steps I can take for you:
- Tune the `detect_columns`/`detect_rows` heuristics for your exact template.
- Add a JSON `grid` file describing cell coordinates for deterministic detection.
- Run the prototype on your attached images and return the CSV + debug overlays.

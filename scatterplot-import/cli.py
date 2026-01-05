#!/usr/bin/env python3
"""CLI prototype: align scanned sheet (image or PDF) to template, detect filled marks, output CSV.

Supports single images (PNG/JPG) or multi-page PDF inputs. For PDFs, each page is processed
and the CSV includes a `page` column. Debug images for each page are written when `--debug`.
"""
import argparse
import csv
from pathlib import Path
import cv2
import numpy as np
from template_align import align_page
from mark_detector import detect_marks

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None


def pil_from_fitz_pixmap(pix):
    # Convert fitz.Pixmap to OpenCV BGR image
    mode = pix.n
    arr = np.frombuffer(pix.samples, dtype=np.uint8)
    if mode == 1:
        img = arr.reshape(pix.height, pix.width)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    else:
        img = arr.reshape(pix.height, pix.width, mode)
        # fitz gives RGB(A); convert to BGR
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img


def image_from_path(path: Path):
    ext = path.suffix.lower()
    if ext == ".pdf":
        if fitz is None:
            raise SystemExit("PyMuPDF is required to read PDFs. Install with 'pip install PyMuPDF'")
        doc = fitz.open(str(path))
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=200)
            img = pil_from_fitz_pixmap(pix)
            yield i + 1, img
    else:
        img = cv2.imread(str(path))
        if img is None:
            raise SystemExit(f"Unable to read image: {path}")
        yield 1, img


def main():
    p = argparse.ArgumentParser(description="Scatterplot import prototype: detect filled cells from image or PDF")
    p.add_argument("input", help="Scanned image file (PNG/JPG) or PDF")
    p.add_argument("--template", help="Template image to align to (optional)")
    p.add_argument("--out", help="CSV output file (for single image) or base name for multi-page", default="output.csv")
    p.add_argument("--out-dir", help="Directory to write per-page outputs/debug images", default=None)
    p.add_argument("--debug", help="Write debug images (warped, overlay)", action="store_true")
    args = p.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    out_dir = Path(args.out_dir) if args.out_dir else in_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for page_num, img in image_from_path(in_path):
        warped, M = align_page(img, template_path=args.template)
        results, debug_img = detect_marks(warped)

        for r, c, filled, frac in results:
            rows.append({"page": page_num, "row": r, "col": c, "filled": int(filled), "fill_fraction": float(frac)})

        if args.debug:
            warped_path = out_dir / f"{in_path.stem}_page{page_num}_warped.png"
            overlay_path = out_dir / f"{in_path.stem}_page{page_num}_debug.png"
            cv2.imwrite(str(warped_path), warped)
            cv2.imwrite(str(overlay_path), debug_img)
            print(f"Wrote debug images: {warped_path}, {overlay_path}")

    # write combined CSV
    out_path = Path(args.out)
    if len(rows) == 0:
        print("No cells detected; no CSV written.")
        return

    # If input was multi-page and out is a filename, append page info in CSV
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["page", "row", "col", "filled", "fill_fraction"])
        for r in rows:
            w.writerow([r["page"], r["row"], r["col"], r["filled"], f"{r['fill_fraction']:.3f}"])

    print(f"Wrote CSV: {out_path}")


if __name__ == "__main__":
    main()

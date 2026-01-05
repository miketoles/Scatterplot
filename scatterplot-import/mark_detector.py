"""Detect filled marks in a warped scatterplot page.

This prototype uses projection profiles to find vertical column separators and horizontal rows,
then computes fill fraction per cell. Returns a list of (row, col, filled, fill_fraction)
and a debug overlay image.
"""
from typing import List, Tuple
import numpy as np
import cv2


def detect_columns(gray: np.ndarray, min_sep=40) -> List[int]:
    # vertical projection
    proj = np.mean(gray, axis=0)
    # smooth
    proj_s = cv2.GaussianBlur(proj.reshape(1, -1).astype('float32'), (1, 51), 0).ravel()
    # find valleys between columns by thresholding
    thresh = np.percentile(proj_s, 65)
    separators = np.where(proj_s > thresh, 0, 1).ravel()
    # find continuous runs of separators and take centers
    cols = []
    i = 0
    W = len(separators)
    while i < W:
        if separators[i] == 1:
            j = i
            while j < W and separators[j] == 1:
                j += 1
            cols.append((i + j) // 2)
            i = j
        else:
            i += 1
    # if detection fails, fallback to 6 evenly spaced column boundaries
    if len(cols) < 2:
        W = gray.shape[1]
        cols = [int(W * i / 6) for i in range(7)]
    return cols


def detect_rows(gray: np.ndarray, min_sep=20) -> List[int]:
    proj = np.mean(gray, axis=1)
    proj_s = cv2.GaussianBlur(proj.reshape(-1, 1).astype('float32'), (51, 1), 0).ravel()
    thresh = np.percentile(proj_s, 60)
    separators = np.where(proj_s > thresh, 0, 1).ravel()
    rows = []
    i = 0
    H = len(separators)
    while i < H:
        if separators[i] == 1:
            j = i
            while j < H and separators[j] == 1:
                j += 1
            rows.append((i + j) // 2)
            i = j
        else:
            i += 1
    if len(rows) < 4:
        H = gray.shape[0]
        rows = [int(H * i / 20) for i in range(21)]
    return rows


def detect_marks(img: np.ndarray, fill_threshold: float = 0.07) -> Tuple[List[Tuple[int, int, bool, float]], np.ndarray]:
    # work on a grayscale, slightly blurred image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    cols = detect_columns(gray)
    rows = detect_rows(gray)

    # Build cell grid from separators: take adjacent pairs
    # If separators are N points, cells = len(cols)-1 x len(rows)-1
    results = []
    debug = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    for r in range(len(rows) - 1):
        y0 = rows[r]
        y1 = rows[r + 1]
        for c in range(len(cols) - 1):
            x0 = cols[c]
            x1 = cols[c + 1]
            cell = gray[y0:y1, x0:x1]
            if cell.size == 0:
                continue
            # compute fraction of dark pixels
            _, th = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            dark = (th == 0).sum()
            frac = dark / float(cell.size)
            filled = frac > fill_threshold
            results.append((r, c, filled, frac))
            # debug rectangle
            color = (0, 255, 0) if not filled else (0, 0, 255)
            cv2.rectangle(debug, (x0, y0), (x1, y1), color, 2)
    return results, debug

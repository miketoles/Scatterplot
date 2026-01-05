"""Simple template alignment utilities.

Approach:
- Try to detect the largest document contour and warp it to a default A4-like aspect ratio.
- If a `template_path` is provided, load the template image and warp the page to the template size.
"""
from typing import Optional, Tuple
import cv2
import numpy as np


def find_page_contour(gray: np.ndarray) -> Optional[np.ndarray]:
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    for c in cnts[:5]:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            return approx.reshape(4, 2)
    return None


def order_points(pts: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def warp_image(img: np.ndarray, pts: np.ndarray, dst_size: Tuple[int, int]) -> np.ndarray:
    rect = order_points(pts)
    (w, h) = dst_size
    dst = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (w, h))
    return warped, M


def align_page(img: np.ndarray, template_path: Optional[str] = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Return (warped_image, homography)

    If `template_path` provided, warp to template's dimensions; otherwise use a 2480x3508 (A4@300dpi) canvas.
    """
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    pts = find_page_contour(gray)
    if template_path:
        tmpl = cv2.imread(template_path)
        th, tw = tmpl.shape[:2]
        dst_size = (tw, th)
    else:
        # default to A4-ish output (portrait)
        dst_size = (2480, 3508)

    if pts is None:
        # fallback: center crop/resize
        warped = cv2.resize(img, dst_size)
        return warped, None

    warped, M = warp_image(img, pts, dst_size)
    return warped, M

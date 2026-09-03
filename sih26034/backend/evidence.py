import cv2
import os
from typing import Optional

def generate_evidence_crop(image_path: str, bbox: list, output_path: str) -> Optional[str]:
    if not os.path.exists(image_path):
        return None
    img = cv2.imread(image_path)
    if img is None:
        return None
    h, w = img.shape[:2]
    if len(bbox) == 4:
        if all(0 <= v <= 1000 for v in bbox) and any(v > 1.0 for v in bbox):
            ymin, xmin, ymax, xmax = bbox
            y1 = int((ymin / 1000.0) * h)
            x1 = int((xmin / 1000.0) * w)
            y2 = int((ymax / 1000.0) * h)
            x2 = int((xmax / 1000.0) * w)
        else:
            ymin, xmin, ymax, xmax = bbox
            y1 = int(ymin * h)
            x1 = int(xmin * w)
            y2 = int(ymax * h)
            x2 = int(xmax * w)
        pad = 20
        cy1, cy2 = max(0, y1 - pad), min(h, y2 + pad)
        cx1, cx2 = max(0, x1 - pad), min(w, x2 + pad)
        crop = img[cy1:cy2, cx1:cx2].copy()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        cv2.imwrite(output_path, crop)
        return output_path
    return None

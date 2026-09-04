import cv2
import numpy as np
import os
from typing import Dict, Any

LAPLACIAN_BLUR_THRESHOLD = float(os.getenv('LAPLACIAN_BLUR_THRESHOLD', 85.0))

def assess_image_quality(image_path: str) -> Dict[str, Any]:
    if not os.path.exists(image_path):
        return {'quality_status': 'ERROR', 'quality_score': 0.0, 'blur_metric': 0.0, 'brightness_metric': 0.0, 'glare_percentage': 0.0, 'usable': False, 'reason': 'File not found'}
    img = cv2.imread(image_path)
    if img is None:
        return {'quality_status': 'UNREADABLE', 'quality_score': 0.0, 'blur_metric': 0.0, 'brightness_metric': 0.0, 'glare_percentage': 0.0, 'usable': False, 'reason': 'Invalid image format'}
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    mean_brightness = float(np.mean(gray))
    glare_pixels = np.sum(gray > 242)
    glare_pct = float((glare_pixels / (h * w)) * 100)
    
    is_blurry = laplacian_var < LAPLACIAN_BLUR_THRESHOLD
    is_too_dark = mean_brightness < 40
    is_glary = glare_pct > 18.0
    
    blur_score = min(1.0, laplacian_var / 250.0)
    brightness_score = 1.0 - abs(mean_brightness - 128) / 128.0
    glare_score = max(0.0, 1.0 - (glare_pct / 20.0))
    quality_score = round(float((blur_score * 0.5) + (brightness_score * 0.3) + (glare_score * 0.2)), 2)
    
    if is_blurry:
        status = 'BLURRY'
        usable = False
    elif is_glary:
        status = 'GLARE'
        usable = False
    elif is_too_dark:
        status = 'TOO_DARK'
        usable = False
    elif quality_score >= 0.75:
        status = 'PASS'
        usable = True
    else:
        status = 'LOW_QUALITY'
        usable = False
        
    return {
        'quality_status': status,
        'quality_score': quality_score,
        'blur_metric': round(laplacian_var, 2),
        'brightness_metric': round(mean_brightness, 2),
        'glare_percentage': round(glare_pct, 2),
        'width': w,
        'height': h,
        'usable': usable
    }

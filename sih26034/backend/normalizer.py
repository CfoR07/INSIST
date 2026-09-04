import re
from typing import Dict, Any, Tuple, Optional

METRIC_UNIT_MAP = {
    'g': 'g', 'gm': 'g', 'gram': 'g', 'grams': 'g', 'gms': 'g',
    'kg': 'kg', 'kgs': 'kg', 'kilogram': 'kg', 'kilograms': 'kg',
    'ml': 'ml', 'm.l.': 'ml', 'millilitre': 'ml', 'millilitres': 'ml', 'milliliter': 'ml',
    'l': 'l', 'ltr': 'l', 'litre': 'l', 'litres': 'l', 'liter': 'l', 'liters': 'l',
    'm': 'm', 'metre': 'm', 'metres': 'm', 'meter': 'm',
    'cm': 'cm', 'centimetre': 'cm',
    'mm': 'mm', 'millimetre': 'mm',
    'n': 'n', 'no': 'n', 'no.': 'n', 'num': 'n', 'number': 'n', 'units': 'units', 'pcs': 'pcs', 'piece': 'pcs', 'pieces': 'pcs'
}

def normalize_quantity(raw_str: Optional[str]) -> Tuple[Optional[float], Optional[str]]:
    if not raw_str:
        return None, None
    clean = raw_str.strip()
    match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z.]+)', clean)
    if not match:
        num_only = re.search(r'([0-9]+(?:\.[0-9]+)?)', clean)
        val = float(num_only.group(1)) if num_only else None
        return val, None
    
    val = float(match.group(1))
    raw_unit = match.group(2).lower().replace('.', '')
    std_unit = METRIC_UNIT_MAP.get(raw_unit, raw_unit)
    return val, std_unit

def normalize_mrp(raw_str: Optional[str]) -> Tuple[Optional[float], str, bool]:
    if not raw_str:
        return None, "INR", True
    clean = raw_str.strip()
    match = re.search(r'([0-9]+(?:\.[0-9]{1,2})?)', clean)
    val = float(match.group(1)) if match else None
    tax_inclusive = bool(re.search(r'(incl|inclusive|tax)', clean, re.IGNORECASE)) or True
    return val, "INR", tax_inclusive

def normalize_date(raw_str: Optional[str]) -> Optional[str]:
    if not raw_str:
        return None
    clean = raw_str.strip()
    d_match = re.search(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})', clean)
    if d_match:
        p1, p2, p3 = d_match.groups()
        yr = p3 if len(p3) == 4 else f"20{p3}"
        return f"{yr}-{int(p2):02d}-{int(p1):02d}"
    my_match = re.search(r'(\d{1,2})[/.-](\d{2,4})', clean)
    if my_match:
        m, y = my_match.groups()
        yr = y if len(y) == 4 else f"20{y}"
        return f"{yr}-{int(m):02d}"
    return clean

import re
from typing import Dict, Any, List, Optional

def build_candidate_rules_from_document(doc_meta: Dict[str, Any], extracted_text: str) -> List[Dict[str, Any]]:
    candidates = []
    doc_id = doc_meta["doc_id"]
    doc_title = doc_meta["title"]
    eff_date = doc_meta["effective_date"]
    
    # Gazette GSR 779(E) USP Amendment
    if "779" in doc_id or "G.S.R. 779" in extracted_text or "Unit Sale Price" in doc_title:
        candidates.append({
            "candidate_id": f"CAND-USP-{doc_id}",
            "rule_id": "RULE-USP-DECLARATION",
            "rule_code": "LMPC-004",
            "version_label": "2022-v2",
            "doc_id": doc_id,
            "statutory_reference": "Rule 6(11) as amended by G.S.R. 779(E)",
            "legal_text": "Every package shall bear the unit sale price in Indian Rupees...",
            "field": "unit_sale_price",
            "validation_type": "presence",
            "operator": "exists",
            "expected_value": None,
            "expected_unit": "INR/unit",
            "condition_expression": '{"exempt_if": ["net_quantity_eq_1kg", "net_quantity_eq_1l", "net_quantity_eq_1m"]}',
            "effective_from": eff_date,
            "effective_until": None,
            "verification_status": "PENDING"
        })
        
    # Gazette GSR 226(E) Electronics QR e-Labelling Amendment
    if "226" in doc_id or "G.S.R. 226" in extracted_text or "Electronic" in doc_title:
        candidates.append({
            "candidate_id": f"CAND-ELEC-QR-{doc_id}",
            "rule_id": "RULE-ELEC-QR-LABEL",
            "rule_code": "LMPC-011",
            "version_label": "2022-v1",
            "doc_id": doc_id,
            "statutory_reference": "Rule 6(1) proviso as amended by G.S.R. 226(E)",
            "legal_text": "Electronic products may declare information through QR Code for 1 year...",
            "field": "electronic_qr_label",
            "validation_type": "presence",
            "operator": "exists",
            "expected_value": None,
            "expected_unit": "QR_CODE",
            "condition_expression": '{"only_if": "category_is_electronics"}',
            "effective_from": eff_date,
            "effective_until": None,
            "verification_status": "PENDING"
        })

    # Gazette GSR 747(E) Loose Garment Amendment
    if "747" in doc_id or "G.S.R. 747" in extracted_text or "Garment" in doc_title:
        candidates.append({
            "candidate_id": f"CAND-GARMENT-AREA-{doc_id}",
            "rule_id": "RULE-GARMENT-AREA",
            "rule_code": "LMPC-012",
            "version_label": "2024-v1",
            "doc_id": doc_id,
            "statutory_reference": "Rule 6(1) Expl. (v) as amended by G.S.R. 747(E)",
            "legal_text": "Garments sold in loose form shall declare Consumer Care, Manufacturer, MRP and Net Qty in dimensions...",
            "field": "net_quantity_dimensions",
            "validation_type": "presence",
            "operator": "exists",
            "expected_value": None,
            "expected_unit": "cm/m",
            "condition_expression": '{"only_if": "commodity_is_garment"}',
            "effective_from": eff_date,
            "effective_until": None,
            "verification_status": "PENDING"
        })
        
    return candidates

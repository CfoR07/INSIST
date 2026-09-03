# Python build runner
import os

with open(r"n:\PROJECTS\INSIST\sih26034\backend\exceptions.py", "w", encoding="utf-8") as f:
    f.write('''from typing import Dict, Any

def check_rule_exemptions(rule: Dict[str, Any], facts_by_field: Dict[str, Any], category: str) -> Dict[str, Any]:
    rule_id = rule.get("rule_id", "")
    rule_cat = rule.get("category", "ALL")
    
    if rule_cat != "ALL" and rule_cat.lower() != category.lower():
        return {
            "applicable": False,
            "exemption_reason": f"Rule applies only to '{rule_cat}', but product category is '{category}'."
        }
        
    net_qty_fact_list = facts_by_field.get("net_quantity", [])
    if net_qty_fact_list:
        net_qty_fact = net_qty_fact_list[0]
        norm_val = net_qty_fact.get("normalized_value")
        unit = str(net_qty_fact.get("unit", "")).lower()
        try:
            val_float = float(norm_val) if norm_val else None
            if val_float is not None and val_float <= 10.0 and unit in ["g", "gm", "ml"]:
                if rule_id in ["LMPC-004", "LMPC-008"]:
                    return {
                        "applicable": False,
                        "exemption_reason": f"Exempt under Rule 26: Small package ({val_float}{unit} <= 10{unit})."
                    }
        except Exception:
            pass
            
    if rule_id == "LMPC-004" and net_qty_fact_list:
        net_qty_fact = net_qty_fact_list[0]
        norm_val = net_qty_fact.get("normalized_value")
        unit = str(net_qty_fact.get("unit", "")).lower()
        try:
            val_float = float(norm_val) if norm_val else None
            if val_float == 1.0 and unit in ["kg", "l", "litre", "liter"]:
                return {
                    "applicable": False,
                    "exemption_reason": "Unit Sale Price declaration not required when package is exactly 1 kg / 1 L."
                }
        except Exception:
            pass

    return {"applicable": True, "exemption_reason": None}
''')

with open(r"n:\PROJECTS\INSIST\sih26034\backend\compliance_engine.py", "w", encoding="utf-8") as f:
    f.write('''import re
from typing import Dict, Any, List

class DeterministicComplianceEngine:
    @staticmethod
    def evaluate_rule(rule: Dict[str, Any], facts_for_field: List[Dict[str, Any]], all_facts: Dict[str, Any]) -> Dict[str, Any]:
        rule_id = rule["rule_id"]
        field = rule["field"]
        v_type = rule["validation_type"]
        operator = rule["operator"]
        
        # Conflict check
        if len(facts_for_field) > 1:
            values = list(set(f.get("value", "") for f in facts_for_field if f.get("value")))
            if len(values) > 1:
                return {
                    "status": "CONFLICT",
                    "observed_value": " vs ".join(values),
                    "reason": f"Conflicting declarations detected across package views: {', '.join(values)}. Manual officer review required.",
                    "evidence_fact_ids": [f["id"] for f in facts_for_field]
                }
                
        if not facts_for_field:
            return {
                "status": "FAIL",
                "observed_value": "NOT FOUND",
                "reason": f"Mandatory statutory declaration '{rule['requirement']}' was not detected in any packaging photograph.",
                "evidence_fact_ids": []
            }
            
        primary_fact = facts_for_field[0]
        status = primary_fact.get("extraction_status", "FOUND")
        val_str = primary_fact.get("value", "")
        norm_val = primary_fact.get("normalized_value")
        confidence = primary_fact.get("confidence", 1.0)
        
        if status == "UNREADABLE":
            return {
                "status": "UNCERTAIN",
                "observed_value": val_str or "UNREADABLE",
                "reason": f"Declaration detected but unreadable (Confidence: {confidence:.2f}).",
                "evidence_fact_ids": [primary_fact["id"]]
            }
            
        if status == "NOT_FOUND":
            return {
                "status": "FAIL",
                "observed_value": "NOT FOUND",
                "reason": f"Mandatory statutory declaration '{rule['requirement']}' is missing.",
                "evidence_fact_ids": [primary_fact["id"]]
            }
            
        if v_type == "presence":
            if val_str and len(val_str.strip()) > 0:
                return {
                    "status": "PASS",
                    "observed_value": val_str,
                    "reason": f"Mandatory statutory declaration present and clearly readable: '{val_str}'.",
                    "evidence_fact_ids": [primary_fact["id"]]
                }
            else:
                return {
                    "status": "FAIL",
                    "observed_value": "EMPTY",
                    "reason": "Statutory declaration field is empty.",
                    "evidence_fact_ids": [primary_fact["id"]]
                }
                
        elif v_type == "format":
            regex_pat = rule.get("expected_value", "")
            if regex_pat and re.search(regex_pat, val_str, re.IGNORECASE):
                return {
                    "status": "PASS",
                    "observed_value": val_str,
                    "reason": "Statutory declaration satisfies required statutory wording and format.",
                    "evidence_fact_ids": [primary_fact["id"]]
                }
            else:
                return {
                    "status": "FAIL",
                    "observed_value": val_str,
                    "reason": f"Format non-compliant. Expected pattern: '{regex_pat}'.",
                    "evidence_fact_ids": [primary_fact["id"]]
                }
                
        elif v_type == "unit_check":
            expected_units = [u.strip().lower() for u in (rule.get("expected_value", "") or "").split(",")]
            unit = (primary_fact.get("unit") or "").lower()
            if not unit:
                for u in expected_units:
                    if re.search(r"\\b" + re.escape(u) + r"\\b", val_str, re.IGNORECASE):
                        unit = u
                        break
            if unit in expected_units:
                return {
                    "status": "PASS",
                    "observed_value": f"{val_str} (Unit: {unit})",
                    "reason": f"Valid standard metric unit '{unit}' declared in accordance with LMPC Schedule.",
                    "evidence_fact_ids": [primary_fact["id"]]
                }
            else:
                return {
                    "status": "FAIL",
                    "observed_value": val_str,
                    "reason": f"Non-standard measurement unit '{unit}'. Must be one of: ({', '.join(expected_units)}).",
                    "evidence_fact_ids": [primary_fact["id"]]
                }
                
        elif v_type == "date_presence":
            date_match = re.search(r"(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4}|\\d{1,2}[/-]\\d{4}|[A-Za-z]{3,9}[\\s,/-]+\\d{2,4}|\\d{2,4})", val_str)
            if date_match or (norm_val and len(str(norm_val)) > 0):
                return {
                    "status": "PASS",
                    "observed_value": val_str,
                    "reason": f"Statutory date declaration verified: '{val_str}'.",
                    "evidence_fact_ids": [primary_fact["id"]]
                }
            else:
                return {
                    "status": "FAIL",
                    "observed_value": val_str,
                    "reason": "Missing or invalid statutory date declaration.",
                    "evidence_fact_ids": [primary_fact["id"]]
                }
                
        return {
            "status": "PASS",
            "observed_value": val_str,
            "reason": f"Requirement verified: {val_str}",
            "evidence_fact_ids": [primary_fact["id"]]
        }
''')

with open(r"n:\PROJECTS\INSIST\sih26034\backend\review_logic.py", "w", encoding="utf-8") as f:
    f.write('''from typing import Dict, Any, List
import os

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.60))

def determine_evidence_sufficiency(compliance_result: Dict[str, Any], facts_for_field: List[Dict[str, Any]]) -> str:
    status = compliance_result.get("status")
    if status in ["CONFLICT", "UNCERTAIN"]:
        return "UNCERTAIN"
    for f in facts_for_field:
        if f.get("confidence", 1.0) < CONFIDENCE_THRESHOLD:
            return "UNCERTAIN"
        if f.get("extraction_status") in ["UNREADABLE", "CONFLICT"]:
            return "UNCERTAIN"
    return "VERIFIABLE"
''')

with open(r"n:\PROJECTS\INSIST\sih26034\backend\evidence.py", "w", encoding="utf-8") as f:
    f.write('''import cv2
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
''')

print("All rule engine and evidence files written successfully")

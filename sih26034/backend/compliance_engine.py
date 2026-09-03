import re
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
                    if re.search(r"\b" + re.escape(u) + r"\b", val_str, re.IGNORECASE):
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
            date_match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}[/-]\d{4}|[A-Za-z]{3,9}[\s,/-]+\d{2,4}|\d{2,4})", val_str)
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

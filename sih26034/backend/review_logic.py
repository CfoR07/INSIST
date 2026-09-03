from typing import Dict, Any, List
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

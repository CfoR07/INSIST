import os
import sys
from typing import Dict, Any, List, Optional
import database as db

def verify_and_activate_candidate_rule(
    candidate: Dict[str, Any],
    officer_id: str,
    human_confirmed_statutory_ref: str,
    human_confirmed_effective_date: str,
    notes: Optional[str] = "Statutory text independently confirmed against official Gazette"
) -> Dict[str, Any]:
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # 1. Ensure parent rule exists
    cursor.execute("SELECT id FROM rules WHERE id = ?", (candidate["rule_id"],))
    rule_exists = cursor.fetchone()
    if not rule_exists:
        cursor.execute(
            "INSERT INTO rules (id, rule_code, category_id, field, requirement, description, severity) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (candidate["rule_id"], candidate["rule_code"], "CAT-ALL", candidate["field"],
             f"Mandatory {candidate['field'].replace('_', ' ').title()} Declaration",
             candidate.get("legal_text", ""), "ERROR")
        )

    # 2. Insert verified rule version
    rv_id = candidate.get("version_id") or f"RV-{candidate['rule_code']}-{candidate['version_label']}"
    cursor.execute(
        """INSERT OR REPLACE INTO rule_versions (
            id, rule_id, version_label, doc_id, statutory_reference, validation_type, operator,
            expected_value, expected_unit, min_value, max_value, condition_expression,
            effective_from, effective_until, verification_status, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'VERIFIED', 1)""",
        (rv_id, candidate["rule_id"], candidate["version_label"], candidate["doc_id"],
         human_confirmed_statutory_ref, candidate["validation_type"], candidate["operator"],
         candidate.get("expected_value"), candidate.get("expected_unit"), candidate.get("min_value"),
         candidate.get("max_value"), candidate.get("condition_expression"),
         human_confirmed_effective_date, candidate.get("effective_until"))
    )
    
    conn.commit()
    conn.close()
    
    return {
        "status": "VERIFIED_AND_ACTIVATED",
        "rule_version_id": rv_id,
        "officer_id": officer_id,
        "statutory_reference": human_confirmed_statutory_ref,
        "effective_from": human_confirmed_effective_date,
        "notes": notes
    }

import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "database", "sih26034.db"))
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
SEED_RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "seed_rules.json")

def get_connection():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
    cursor.execute("SELECT COUNT(*) FROM rules")
    count = cursor.fetchone()[0]
    if count == 0 and os.path.exists(SEED_RULES_PATH):
        with open(SEED_RULES_PATH, "r", encoding="utf-8") as f:
            rules = json.load(f)
            for r in rules:
                cursor.execute(
                    "INSERT OR REPLACE INTO rules (rule_id, category, field, requirement, condition, validation_type, operator, expected_value, expected_unit, min_value, max_value, source_reference, effective_date, version, superseded) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (r["rule_id"], r["category"], r["field"], r["requirement"], r.get("condition"),
                     r["validation_type"], r["operator"], r.get("expected_value"), r.get("expected_unit"),
                     r.get("min_value"), r.get("max_value"), r["source_reference"], r["effective_date"],
                     r["version"], r.get("superseded", 0))
                )
    conn.commit()
    conn.close()

def create_inspection(data: Dict[str, Any]) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inspections (id, product_name, brand, category, package_type, officer_id, timestamp, location, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (data["id"], data.get("product_name", "Unnamed Product"), data.get("brand", ""),
         data.get("category", "ALL"), data.get("package_type", "Pre-Packed Box/Pouch"),
         data.get("officer_id", "OFFICER-001"), data.get("timestamp", datetime.now().isoformat()),
         data.get("location", "Zonal Enforcement Office"), data.get("status", "DRAFT"), data.get("notes", ""))
    )
    conn.commit()
    conn.close()
    return data["id"]

def get_inspection(inspection_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inspections WHERE id = ?", (inspection_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_inspections() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inspections ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_inspection_status(inspection_id: str, status: str, product_name: str = None, category: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    updates = ["status = ?"]
    params = [status]
    if product_name:
        updates.append("product_name = ?")
        params.append(product_name)
    if category:
        updates.append("category = ?")
        params.append(category)
    params.append(inspection_id)
    cursor.execute(f"UPDATE inspections SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()

def save_image_record(data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO images (id, inspection_id, image_url, file_path, view_type, quality_status, quality_score, blur_metric, brightness_metric) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (data["id"], data["inspection_id"], data["image_url"], data["file_path"],
         data["view_type"], data["quality_status"], data["quality_score"],
         data["blur_metric"], data["brightness_metric"])
    )
    conn.commit()
    conn.close()

def get_inspection_images(inspection_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM images WHERE inspection_id = ? ORDER BY created_at ASC", (inspection_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_extracted_facts(inspection_id: str, facts: List[Dict[str, Any]]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM extracted_facts WHERE inspection_id = ?", (inspection_id,))
    for f in facts:
        bbox_str = json.dumps(f.get("bounding_box", []))
        cursor.execute(
            "INSERT INTO extracted_facts (id, inspection_id, field_name, value, normalized_value, unit, confidence, extraction_status, bounding_box, source_image_id, source_view_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f["id"], inspection_id, f["field_name"], f.get("value"),
             str(f.get("normalized_value", "")), f.get("unit"), f.get("confidence", 1.0),
             f.get("extraction_status", "FOUND"), bbox_str, f.get("source_image_id"), f.get("source_view_type"))
        )
    conn.commit()
    conn.close()

def get_extracted_facts(inspection_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM extracted_facts WHERE inspection_id = ?", (inspection_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        if d["bounding_box"]:
            try:
                d["bounding_box"] = json.loads(d["bounding_box"])
            except Exception:
                pass
        result.append(d)
    return result

def get_applicable_rules(category: str = "ALL", inspection_date: str = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if not inspection_date:
        inspection_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT * FROM rules WHERE (category = 'ALL' OR category = ?) AND superseded = 0 AND effective_date <= ? ORDER BY rule_id ASC",
        (category, inspection_date)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_compliance_results(inspection_id: str, results: List[Dict[str, Any]]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM compliance_results WHERE inspection_id = ?", (inspection_id,))
    for r in results:
        fact_ids_str = json.dumps(r.get("evidence_fact_ids", []))
        cursor.execute(
            "INSERT INTO compliance_results (id, inspection_id, rule_id, field, status, observed_value, reason, evidence_fact_ids, review_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (r["id"], inspection_id, r["rule_id"], r["field"], r["status"],
             r.get("observed_value"), r["reason"], fact_ids_str, r.get("review_status", "VERIFIABLE"))
        )
    conn.commit()
    conn.close()

def get_compliance_results(inspection_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT cr.*, r.requirement, r.condition, r.source_reference, r.validation_type, r.operator FROM compliance_results cr JOIN rules r ON cr.rule_id = r.rule_id WHERE cr.inspection_id = ? ORDER BY cr.rule_id ASC",
        (inspection_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    res = []
    for r in rows:
        d = dict(r)
        if d["evidence_fact_ids"]:
            try:
                d["evidence_fact_ids"] = json.loads(d["evidence_fact_ids"])
            except Exception:
                pass
        res.append(d)
    return res

def save_review_decision(data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO review_decisions (id, compliance_result_id, inspection_id, officer_id, decision, edited_value, note, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (data["id"], data["compliance_result_id"], data["inspection_id"],
         data.get("officer_id", "OFFICER-001"), data["decision"],
         data.get("edited_value"), data.get("note", ""),
         data.get("timestamp", datetime.now().isoformat()))
    )
    cursor.execute("UPDATE compliance_results SET review_status = ? WHERE id = ?", ("VERIFIABLE", data["compliance_result_id"]))
    conn.commit()
    conn.close()

def get_review_decisions(inspection_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM review_decisions WHERE inspection_id = ?", (inspection_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_dashboard_metrics():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inspections")
    total_inspections = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM compliance_results WHERE status = 'PASS'")
    total_pass = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM compliance_results WHERE status = 'FAIL'")
    total_fail = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM compliance_results WHERE status = 'UNCERTAIN' OR status = 'CONFLICT'")
    total_uncertain = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM compliance_results WHERE review_status = 'UNCERTAIN'")
    pending_reviews = cursor.fetchone()[0]
    cursor.execute(
        "SELECT cr.rule_id, r.requirement, COUNT(*) as count FROM compliance_results cr JOIN rules r ON cr.rule_id = r.rule_id WHERE cr.status = 'FAIL' GROUP BY cr.rule_id ORDER BY count DESC LIMIT 5"
    )
    common_violations = [{"rule_id": r[0], "requirement": r[1], "count": r[2]} for r in cursor.fetchall()]
    cursor.execute("SELECT category, COUNT(*) as count FROM inspections GROUP BY category")
    category_counts = [{"category": r[0], "count": r[1]} for r in cursor.fetchall()]
    conn.close()
    return {
        "total_inspections": total_inspections,
        "pass_count": total_pass,
        "fail_count": total_fail,
        "uncertain_count": total_uncertain,
        "pending_reviews": pending_reviews,
        "common_violations": common_violations,
        "category_counts": category_counts
    }


def delete_image_record(inspection_id: str, image_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM inspection_images WHERE id = ? AND inspection_id = ?", (image_id, inspection_id))
    c.execute("DELETE FROM extracted_facts WHERE source_image_id = ? AND inspection_id = ?", (image_id, inspection_id))
    conn.commit()
    conn.close()

def clear_inspection_images(inspection_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM inspection_images WHERE inspection_id = ?", (inspection_id,))
    c.execute("DELETE FROM extracted_facts WHERE inspection_id = ?", (inspection_id,))
    c.execute("DELETE FROM compliance_results WHERE inspection_id = ?", (inspection_id,))
    conn.commit()
    conn.close()

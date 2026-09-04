import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "database", "sih26034.db"))
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
SEED_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "seed_data_v2.json")

def get_connection():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
    
    # Check if seed data exists
    cursor.execute("SELECT COUNT(*) FROM rules")
    count = cursor.fetchone()[0]
    if count == 0 and os.path.exists(SEED_DATA_PATH):
        with open(SEED_DATA_PATH, "r", encoding="utf-8") as f:
            seed = json.load(f)
            
            # 1. Categories
            for cat in seed.get("categories", []):
                cursor.execute(
                    "INSERT OR REPLACE INTO categories (id, name, parent_id, description) VALUES (?, ?, ?, ?)",
                    (cat["id"], cat["name"], cat.get("parent_id"), cat.get("description"))
                )
                
            # 2. Regulatory Documents
            for doc in seed.get("regulatory_documents", []):
                cursor.execute(
                    "INSERT OR REPLACE INTO regulatory_documents (id, authority, title, notification_number, publication_date, effective_date, source_url, document_hash, verification_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (doc["id"], doc["authority"], doc["title"], doc.get("notification_number"), doc["publication_date"], doc["effective_date"], doc.get("source_url"), doc.get("document_hash"), doc.get("verification_status", "VERIFIED"))
                )
                
            # 3. Rules
            for r in seed.get("rules", []):
                cursor.execute(
                    "INSERT OR REPLACE INTO rules (id, rule_code, category_id, field, requirement, description, severity) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (r["id"], r["rule_code"], r["category_id"], r["field"], r["requirement"], r.get("description"), r.get("severity", "ERROR"))
                )
                
            # 4. Rule Versions
            for rv in seed.get("rule_versions", []):
                cursor.execute(
                    "INSERT OR REPLACE INTO rule_versions (id, rule_id, version_label, doc_id, statutory_reference, validation_type, operator, expected_value, expected_unit, min_value, max_value, condition_expression, effective_from, effective_until, verification_status, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (rv["id"], rv["rule_id"], rv["version_label"], rv["doc_id"], rv["statutory_reference"], rv["validation_type"], rv["operator"], rv.get("expected_value"), rv.get("expected_unit"), rv.get("min_value"), rv.get("max_value"), rv.get("condition_expression"), rv["effective_from"], rv.get("effective_until"), rv.get("verification_status", "VERIFIED"), rv.get("is_active", 1))
                )
                
    conn.commit()
    conn.close()

# ----------------- Category Taxonomy -----------------
def get_all_categories() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_category_by_id(category_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# ----------------- Inspections -----------------
def create_inspection(data: Dict[str, Any]) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cat_id = data.get("category_id") or "CAT-ALL"
    cursor.execute(
        "INSERT INTO inspections (id, product_name, brand, category_id, package_type, officer_id, inspection_date, location, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (data["id"], data.get("product_name", "Pre-Packed Commodity Sample"), data.get("brand", ""),
         cat_id, data.get("package_type", "Pouch / Box"),
         data.get("officer_id", "OFFICER-001"), data.get("inspection_date", datetime.now().isoformat()),
         data.get("location", "Zonal Enforcement Lab"), data.get("status", "DRAFT"), data.get("notes", ""))
    )
    conn.commit()
    conn.close()
    return data["id"]

def get_inspection(inspection_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.*, c.name as category_name 
        FROM inspections i 
        LEFT JOIN categories c ON i.category_id = c.id 
        WHERE i.id = ?
    ''', (inspection_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_inspections() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.*, c.name as category_name 
        FROM inspections i 
        LEFT JOIN categories c ON i.category_id = c.id 
        ORDER BY i.created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_inspection_status(inspection_id: str, status: str, product_name: str = None, category_id: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    updates = ["status = ?"]
    params = [status]
    if product_name:
        updates.append("product_name = ?")
        params.append(product_name)
    if category_id:
        updates.append("category_id = ?")
        params.append(category_id)
    params.append(inspection_id)
    cursor.execute(f"UPDATE inspections SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()

# ----------------- Images -----------------
def save_image_record(data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO images (id, inspection_id, image_url, storage_path, file_path, view_type, quality_status, quality_score, blur_metric, brightness_metric, glare_percentage, usable) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (data["id"], data["inspection_id"], data["image_url"], data.get("storage_path"), data["file_path"],
         data["view_type"], data["quality_status"], data["quality_score"],
         data["blur_metric"], data["brightness_metric"], data.get("glare_percentage", 0.0), data.get("usable", 1))
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

def delete_image_record(inspection_id: str, image_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM images WHERE inspection_id = ? AND id = ?", (inspection_id, image_id))
    cursor.execute("DELETE FROM ocr_results WHERE image_id = ?", (image_id,))
    conn.commit()
    conn.close()

def clear_inspection_images(inspection_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM images WHERE inspection_id = ?", (inspection_id,))
    cursor.execute("DELETE FROM ocr_results WHERE inspection_id = ?", (inspection_id,))
    conn.commit()
    conn.close()

# ----------------- Raw OCR Persistence -----------------
def save_ocr_result(data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO ocr_results (id, inspection_id, image_id, raw_text, tokens_json, mean_confidence, ocr_engine) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (data["id"], data["inspection_id"], data["image_id"], data["raw_text"],
         json.dumps(data.get("tokens", [])) if isinstance(data.get("tokens"), (list, dict)) else data.get("tokens_json", "[]"),
         data.get("mean_confidence", 1.0), data.get("ocr_engine", "WinOCR/PaddleOCR"))
    )
    conn.commit()
    conn.close()

def get_ocr_results(inspection_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ocr_results WHERE inspection_id = ? ORDER BY created_at ASC", (inspection_id,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        if d.get("tokens_json"):
            try:
                d["tokens"] = json.loads(d["tokens_json"])
            except Exception:
                d["tokens"] = []
        results.append(d)
    return results

# ----------------- Canonical Structured Product Data -----------------
def save_structured_product_data(inspection_id: str, data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    spd_id = f"SPD-{inspection_id}"
    cursor.execute("DELETE FROM structured_product_data WHERE inspection_id = ?", (inspection_id,))
    
    qty = data.get("net_quantity") or {}
    mrp = data.get("mrp") or {}
    usp = data.get("unit_sale_price") or {}
    mfg = data.get("manufacture_date") or {}
    exp = data.get("expiry_date") or {}
    cc = data.get("consumer_care") or {}
    
    cursor.execute(
        '''INSERT INTO structured_product_data (
            id, inspection_id, product_name, brand, category_id,
            manufacturer_name, manufacturer_address, packer_name, packer_address,
            importer_name, importer_address, country_of_origin,
            net_quantity_value, net_quantity_unit, net_quantity_raw,
            mrp_value, mrp_currency, mrp_tax_inclusive, mrp_raw,
            unit_sale_price_value, unit_sale_price_unit, unit_sale_price_raw,
            mfg_date_raw, mfg_date_normalized, expiry_date_raw, expiry_date_normalized,
            batch_number, consumer_care_email, consumer_care_phone, consumer_care_address,
            veg_nonveg_status, extraction_confidence, raw_schema_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            spd_id, inspection_id, data.get("product_name"), data.get("brand"), data.get("category_id", "CAT-ALL"),
            data.get("manufacturer_name"), data.get("manufacturer_address"), data.get("packer_name"), data.get("packer_address"),
            data.get("importer_name"), data.get("importer_address"), data.get("country_of_origin"),
            qty.get("normalized_value"), qty.get("unit"), qty.get("raw_value"),
            mrp.get("normalized_value"), mrp.get("currency", "INR"), 1 if mrp.get("tax_inclusive", True) else 0, mrp.get("raw_value"),
            usp.get("normalized_value"), usp.get("unit"), usp.get("raw_value"),
            mfg.get("raw_value"), mfg.get("normalized_value"), exp.get("raw_value"), exp.get("normalized_value"),
            data.get("batch_number"), cc.get("email"), cc.get("phone"), cc.get("address"),
            data.get("veg_nonveg_status", "NONE"), data.get("extraction_confidence", 1.0),
            json.dumps(data)
        )
    )
    conn.commit()
    conn.close()

def get_structured_product_data(inspection_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM structured_product_data WHERE inspection_id = ?", (inspection_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    if d.get("raw_schema_json"):
        try:
            d["schema"] = json.loads(d["raw_schema_json"])
        except Exception:
            pass
    return d

# ----------------- Versioned Rules Retrieval -----------------
def get_applicable_rules(category_id: str = "CAT-ALL", inspection_date: str = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if not inspection_date:
        inspection_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('''
        SELECT 
            r.id as rule_id,
            r.rule_code,
            r.category_id,
            r.field,
            r.requirement,
            r.description as rule_description,
            r.severity,
            rv.id as rule_version_id,
            rv.version_label,
            rv.doc_id,
            rv.statutory_reference,
            rv.validation_type,
            rv.operator,
            rv.expected_value,
            rv.expected_unit,
            rv.min_value,
            rv.max_value,
            rv.condition_expression,
            rv.effective_from,
            rv.effective_until,
            rv.verification_status,
            d.title as document_title,
            d.notification_number,
            d.authority as issuing_authority
        FROM rules r
        JOIN rule_versions rv ON r.id = rv.rule_id
        JOIN regulatory_documents d ON rv.doc_id = d.id
        WHERE (r.category_id = 'CAT-ALL' OR r.category_id = ?)
          AND rv.is_active = 1
          AND rv.effective_from <= ?
          AND (rv.effective_until IS NULL OR rv.effective_until >= ?)
        ORDER BY r.rule_code ASC
    ''', (category_id, inspection_date, inspection_date))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ----------------- Compliance Violations & Evidence -----------------
def save_compliance_violations(inspection_id: str, violations: List[Dict[str, Any]]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM compliance_violations WHERE inspection_id = ?", (inspection_id,))
    for v in violations:
        bbox_str = json.dumps(v.get("evidence_bounding_box", [])) if isinstance(v.get("evidence_bounding_box"), (list, dict)) else v.get("evidence_bounding_box")
        cursor.execute(
            '''INSERT INTO compliance_violations (
                id, inspection_id, rule_version_id, rule_code, field, status, observed_value, expected_value, reason, severity, evidence_ocr_id, evidence_bounding_box, statutory_reference, review_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (v["id"], inspection_id, v["rule_version_id"], v["rule_code"], v["field"], v["status"],
             v.get("observed_value"), v.get("expected_value"), v["reason"], v.get("severity", "ERROR"),
             v.get("evidence_ocr_id"), bbox_str, v["statutory_reference"], v.get("review_status", "VERIFIABLE"))
        )
    conn.commit()
    conn.close()

def get_compliance_violations(inspection_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM compliance_violations WHERE inspection_id = ? ORDER BY rule_code ASC", (inspection_id,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        if d.get("evidence_bounding_box"):
            try:
                d["evidence_bounding_box"] = json.loads(d["evidence_bounding_box"])
            except Exception:
                pass
        results.append(d)
    return results

# ----------------- Review Decisions -----------------
def save_review_decision(data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO review_decisions (id, inspection_id, violation_id, officer_id, decision, edited_value, note, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (data["id"], data["inspection_id"], data["violation_id"], data["officer_id"], data["decision"],
         data.get("edited_value"), data.get("note"), data.get("timestamp", datetime.now().isoformat()))
    )
    cursor.execute("UPDATE compliance_violations SET review_status = 'OFFICER_CONFIRMED' WHERE id = ?", (data["violation_id"],))
    conn.commit()
    conn.close()

def get_review_decisions(inspection_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM review_decisions WHERE inspection_id = ?", (inspection_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Backward compatibility aliases
save_compliance_results = save_compliance_violations
get_compliance_results = get_compliance_violations

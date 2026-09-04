import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend", "regulatory_ingestion"))

import database as db
from sources import OFFICIAL_SOURCES
from fetcher import fetch_and_store_document, compute_sha256
from document_parser import extract_document_text, parse_metadata_and_clauses
from rule_builder import build_candidate_rules_from_document
from verifier import verify_and_activate_candidate_rule

@pytest.fixture(autouse=True)
def setup_db():
    db_file = os.path.join(os.path.dirname(__file__), "test_regulatory.db")
    if os.path.exists(db_file):
        os.remove(db_file)
    db.DB_PATH = db_file
    db.init_db()
    yield
    if os.path.exists(db_file):
        os.remove(db_file)

# 1. Test official sources registry
def test_official_sources_registry():
    assert len(OFFICIAL_SOURCES) >= 4
    for src in OFFICIAL_SOURCES:
        assert src["source_url"].startswith("http")
        assert "authority" in src
        assert "publication_date" in src

# 2. Test Document Fetch & Storage
def test_document_fetch_and_storage():
    src = OFFICIAL_SOURCES[1] # GSR 779(E)
    doc_res = fetch_and_store_document(src)
    assert doc_res["sha256"] is not None
    assert len(doc_res["sha256"]) == 64
    assert os.path.exists(doc_res["document_storage_path"])

# 3. Test Change Detection (Unchanged SHA256)
def test_change_detection_duplicate_sha():
    src = OFFICIAL_SOURCES[1]
    doc_res1 = fetch_and_store_document(src)
    doc_res2 = fetch_and_store_document(src)
    assert doc_res2["is_unchanged"] is True
    assert doc_res1["sha256"] == doc_res2["sha256"]

# 4. Test Text & Metadata Extraction
def test_document_text_and_clause_extraction():
    src = OFFICIAL_SOURCES[1]
    doc_res = fetch_and_store_document(src)
    text = extract_document_text(doc_res["document_storage_path"])
    assert len(text) > 0
    parsed = parse_metadata_and_clauses(text)
    assert "notification_number" in parsed

# 5. Test Candidate Rule Generation Remains PENDING
def test_candidate_rule_generation_is_pending():
    src = OFFICIAL_SOURCES[1]
    doc_res = fetch_and_store_document(src)
    text = extract_document_text(doc_res["document_storage_path"])
    candidates = build_candidate_rules_from_document(doc_res, text)
    assert len(candidates) >= 1
    for c in candidates:
        assert c["verification_status"] == "PENDING"
        assert c["effective_from"] is not None

# 6. Test Human Verification & Rule Activation
def test_human_verification_and_activation():
    src = OFFICIAL_SOURCES[1]
    doc_res = fetch_and_store_document(src)
    text = extract_document_text(doc_res["document_storage_path"])
    candidates = build_candidate_rules_from_document(doc_res, text)
    usp_candidate = candidates[0]
    
    # Save document into DB first
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO regulatory_documents (id, authority, title, notification_number, publication_date, effective_date, source_url, document_hash, verification_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (doc_res["doc_id"], doc_res["authority"], doc_res["title"], doc_res.get("notification_number"), doc_res["publication_date"], doc_res["effective_date"], doc_res["source_url"], doc_res["sha256"], "VERIFIED")
    )
    conn.commit()
    conn.close()

    # Officer manually confirms legal text against official gazette
    activation_res = verify_and_activate_candidate_rule(
        candidate=usp_candidate,
        officer_id="OFFICER-LEGAL-AUDITOR",
        human_confirmed_statutory_ref="Rule 6(11) as amended by G.S.R. 779(E)",
        human_confirmed_effective_date="2022-12-01",
        notes="Verified against official Gazette G.S.R. 779(E) dated 02-11-2021"
    )
    
    assert activation_res["status"] == "VERIFIED_AND_ACTIVATED"
    
    # Check that rule is now retrievable in active compliance engine
    applicable = db.get_applicable_rules("CAT-ALL", "2023-01-01")
    usp_rule = next((r for r in applicable if r["rule_code"] == "LMPC-004"), None)
    assert usp_rule is not None
    assert usp_rule["verification_status"] == "VERIFIED"
    assert usp_rule["is_active"] == 1

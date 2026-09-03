
-- SIH26034 Master Database Schema
-- Legal Metrology Packaged Commodities Inspection System

CREATE TABLE IF NOT EXISTS inspections (
    id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    brand TEXT,
    category TEXT NOT NULL,
    package_type TEXT,
    officer_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    location TEXT,
    status TEXT NOT NULL DEFAULT 'DRAFT',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS images (
    id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL,
    image_url TEXT NOT NULL,
    file_path TEXT NOT NULL,
    view_type TEXT NOT NULL,
    quality_status TEXT NOT NULL,
    quality_score REAL NOT NULL,
    blur_metric REAL NOT NULL,
    brightness_metric REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(inspection_id) REFERENCES inspections(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS extracted_facts (
    id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL,
    field_name TEXT NOT NULL,
    value TEXT,
    normalized_value TEXT,
    unit TEXT,
    confidence REAL NOT NULL,
    extraction_status TEXT NOT NULL,
    bounding_box TEXT,
    source_image_id TEXT,
    source_view_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(inspection_id) REFERENCES inspections(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rules (
    rule_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    field TEXT NOT NULL,
    requirement TEXT NOT NULL,
    condition TEXT,
    validation_type TEXT NOT NULL,
    operator TEXT NOT NULL,
    expected_value TEXT,
    expected_unit TEXT,
    min_value REAL,
    max_value REAL,
    source_reference TEXT NOT NULL,
    effective_date TEXT NOT NULL,
    version TEXT NOT NULL,
    superseded INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS compliance_results (
    id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    field TEXT NOT NULL,
    status TEXT NOT NULL,
    observed_value TEXT,
    reason TEXT NOT NULL,
    evidence_fact_ids TEXT,
    review_status TEXT NOT NULL DEFAULT 'VERIFIABLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    FOREIGN KEY(rule_id) REFERENCES rules(rule_id)
);

CREATE TABLE IF NOT EXISTS review_decisions (
    id TEXT PRIMARY KEY,
    compliance_result_id TEXT NOT NULL,
    inspection_id TEXT NOT NULL,
    officer_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    edited_value TEXT,
    note TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(compliance_result_id) REFERENCES compliance_results(id) ON DELETE CASCADE
);

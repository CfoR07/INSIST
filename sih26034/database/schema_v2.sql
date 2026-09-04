-- SIH26034 / INSIST Canonical Master Database Schema v2
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    parent_id TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS regulatory_documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    issuing_authority TEXT NOT NULL,
    gazette_notification_no TEXT,
    publication_date TEXT NOT NULL,
    effective_date TEXT NOT NULL,
    source_url TEXT,
    is_verified INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rules (
    id TEXT PRIMARY KEY,
    rule_code TEXT NOT NULL UNIQUE,
    category_id TEXT NOT NULL,
    field TEXT NOT NULL,
    requirement_name TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'CRITICAL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS rule_versions (
    id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL,
    version_label TEXT NOT NULL,
    document_id TEXT NOT NULL,
    statutory_reference TEXT NOT NULL,
    validation_type TEXT NOT NULL,
    operator TEXT NOT NULL,
    machine_readable_logic TEXT NOT NULL,
    effective_from TEXT NOT NULL,
    effective_until TEXT,
    verification_status TEXT NOT NULL DEFAULT 'VERIFIED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(rule_id) REFERENCES rules(id) ON DELETE CASCADE,
    FOREIGN KEY(document_id) REFERENCES regulatory_documents(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS inspections (
    id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    brand TEXT,
    category_id TEXT NOT NULL,
    package_type TEXT,
    officer_id TEXT NOT NULL,
    location TEXT,
    status TEXT NOT NULL DEFAULT 'DRAFT',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE RESTRICT
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
    glare_percentage REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(inspection_id) REFERENCES inspections(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ocr_results (
    id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL,
    image_id TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    raw_ocr_json TEXT NOT NULL,
    confidence REAL NOT NULL,
    engine_info TEXT NOT NULL DEFAULT 'WinOCR/PaddleOCR-MultiPass',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    FOREIGN KEY(image_id) REFERENCES images(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS structured_product_data (
    id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL UNIQUE,
    canonical_product_json TEXT NOT NULL,
    confidence REAL NOT NULL,
    extraction_source TEXT NOT NULL DEFAULT 'Gemini-NLP-Normalizer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(inspection_id) REFERENCES inspections(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS compliance_violations (
    id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL,
    rule_version_id TEXT NOT NULL,
    field TEXT NOT NULL,
    status TEXT NOT NULL,
    observed_value TEXT,
    expected_value TEXT,
    reason TEXT NOT NULL,
    ocr_evidence_id TEXT,
    bounding_box TEXT,
    statutory_reference TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    FOREIGN KEY(rule_version_id) REFERENCES rule_versions(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS review_decisions (
    id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL,
    violation_id TEXT NOT NULL,
    officer_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    edited_value TEXT,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    FOREIGN KEY(violation_id) REFERENCES compliance_violations(id) ON DELETE CASCADE
);

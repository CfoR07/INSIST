-- ====================================================================
-- SIH26034 Master PostgreSQL & SQLite Compatible Schema (v2.0)
-- Pre-Packed Commodity Compliance Verification System (INSIST)
-- ====================================================================

-- 1. CONTROLLED PRODUCT CATEGORY TAXONOMY
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    parent_id TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- 2. REGULATORY KNOWLEDGE DOCUMENTS (Official Gazettes & Acts)
CREATE TABLE IF NOT EXISTS regulatory_documents (
    id TEXT PRIMARY KEY,
    authority TEXT NOT NULL,
    title TEXT NOT NULL,
    notification_number TEXT,
    publication_date DATE NOT NULL,
    effective_date DATE NOT NULL,
    source_url TEXT,
    document_hash TEXT,
    verification_status TEXT NOT NULL DEFAULT 'VERIFIED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. CORE STATUTORY RULES
CREATE TABLE IF NOT EXISTS rules (
    id TEXT PRIMARY KEY,
    rule_code TEXT NOT NULL UNIQUE,
    category_id TEXT NOT NULL,
    field TEXT NOT NULL,
    requirement TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL DEFAULT 'ERROR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- 4. VERSIONED STATUTORY RULES (Effective Date Ranges & Machine-Readable Logic)
CREATE TABLE IF NOT EXISTS rule_versions (
    id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL,
    version_label TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    statutory_reference TEXT NOT NULL,
    validation_type TEXT NOT NULL,
    operator TEXT NOT NULL,
    expected_value TEXT,
    expected_unit TEXT,
    min_value REAL,
    max_value REAL,
    condition_expression TEXT,
    effective_from DATE NOT NULL,
    effective_until DATE,
    verification_status TEXT NOT NULL DEFAULT 'VERIFIED',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE,
    FOREIGN KEY (doc_id) REFERENCES regulatory_documents(id) ON DELETE RESTRICT
);

-- 5. INSPECTION SESSIONS
CREATE TABLE IF NOT EXISTS inspections (
    id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    brand TEXT,
    category_id TEXT NOT NULL,
    package_type TEXT,
    officer_id TEXT NOT NULL,
    inspection_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    location TEXT,
    status TEXT NOT NULL DEFAULT 'DRAFT',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- 6. INSPECTION IMAGES & QUALITY GATE
CREATE TABLE IF NOT EXISTS images (
    id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL,
    image_url TEXT NOT NULL,
    storage_path TEXT,
    file_path TEXT NOT NULL,
    view_type TEXT NOT NULL,
    quality_status TEXT NOT NULL,
    quality_score REAL NOT NULL,
    blur_metric REAL NOT NULL,
    brightness_metric REAL NOT NULL,
    glare_percentage REAL NOT NULL DEFAULT 0.0,
    usable INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE
);

-- 7. RAW OCR RESULTS & SPATIAL BOUNDING BOXES (Full Persistence)
CREATE TABLE IF NOT EXISTS ocr_results (
    id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL,
    image_id TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    tokens_json TEXT,
    mean_confidence REAL NOT NULL,
    ocr_engine TEXT NOT NULL DEFAULT 'WinOCR/PaddleOCR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

-- 8. CANONICAL STRUCTURED PRODUCT DATA (Normalized Entities)
CREATE TABLE IF NOT EXISTS structured_product_data (
    id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL UNIQUE,
    product_name TEXT,
    brand TEXT,
    category_id TEXT NOT NULL,
    manufacturer_name TEXT,
    manufacturer_address TEXT,
    packer_name TEXT,
    packer_address TEXT,
    importer_name TEXT,
    importer_address TEXT,
    country_of_origin TEXT,
    net_quantity_value REAL,
    net_quantity_unit TEXT,
    net_quantity_raw TEXT,
    mrp_value REAL,
    mrp_currency TEXT DEFAULT 'INR',
    mrp_tax_inclusive INTEGER DEFAULT 1,
    mrp_raw TEXT,
    unit_sale_price_value REAL,
    unit_sale_price_unit TEXT,
    unit_sale_price_raw TEXT,
    mfg_date_raw TEXT,
    mfg_date_normalized TEXT,
    expiry_date_raw TEXT,
    expiry_date_normalized TEXT,
    batch_number TEXT,
    consumer_care_email TEXT,
    consumer_care_phone TEXT,
    consumer_care_address TEXT,
    veg_nonveg_status TEXT,
    extraction_confidence REAL NOT NULL DEFAULT 1.0,
    raw_schema_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- 9. COMPLIANCE VIOLATIONS & DETERMINISTIC AUDIT EVIDENCE
CREATE TABLE IF NOT EXISTS compliance_violations (
    id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL,
    rule_version_id TEXT NOT NULL,
    rule_code TEXT NOT NULL,
    field TEXT NOT NULL,
    status TEXT NOT NULL,
    observed_value TEXT,
    expected_value TEXT,
    reason TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'ERROR',
    evidence_ocr_id TEXT,
    evidence_bounding_box TEXT,
    statutory_reference TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'VERIFIABLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    FOREIGN KEY (rule_version_id) REFERENCES rule_versions(id) ON DELETE RESTRICT
);

-- 10. OFFICER REVIEW DECISIONS & AUDIT TRAILS
CREATE TABLE IF NOT EXISTS review_decisions (
    id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL,
    violation_id TEXT NOT NULL,
    officer_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    edited_value TEXT,
    note TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    FOREIGN KEY (violation_id) REFERENCES compliance_violations(id) ON DELETE CASCADE
);

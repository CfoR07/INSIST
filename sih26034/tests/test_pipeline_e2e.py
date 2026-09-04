import os
import sys
import json
import pytest

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import database as db
from models import ProductSchema, QuantityDeclaration, PriceDeclaration, UnitSalePriceDeclaration, DateDeclaration, ConsumerCareDeclaration
import normalizer as norm
from compliance_engine import DeterministicComplianceEngine
import extraction as ext

@pytest.fixture(autouse=True)
def setup_db():
    db_file = os.path.join(os.path.dirname(__file__), "test_sih26034.db")
    if os.path.exists(db_file):
        os.remove(db_file)
    db.DB_PATH = db_file
    db.init_db()
    yield
    if os.path.exists(db_file):
        os.remove(db_file)

# 1. Test ProductSchema validation
def test_product_schema_validation():
    p = ProductSchema(
        product_name="Kellogg's Chocos",
        brand="Kellogg's",
        category_id="CAT-FOOD",
        category_name="Food & Beverages",
        net_quantity=QuantityDeclaration(raw_value="250g", normalized_value=250.0, unit="g", confidence=0.95),
        mrp=PriceDeclaration(raw_value="Rs. 120.00", normalized_value=120.0, currency="INR", tax_inclusive=True),
        unit_sale_price=UnitSalePriceDeclaration(raw_value="Rs 0.48/g", normalized_value=0.48, unit="Rs/g"),
        manufacture_date=DateDeclaration(raw_value="12/2024", normalized_value="2024-12"),
        expiry_date=DateDeclaration(raw_value="12/2025", normalized_value="2025-12"),
        consumer_care=ConsumerCareDeclaration(raw_value="care@kelloggs.com", email="care@kelloggs.com"),
        manufacturer_name="Kellogg India Pvt Ltd, Mumbai",
        veg_nonveg_status="VEG"
    )
    assert p.product_name == "Kellogg's Chocos"
    assert p.net_quantity.normalized_value == 250.0
    assert p.net_quantity.unit == "g"
    assert p.mrp.normalized_value == 120.0

# 2. Test Normalization Helpers
def test_normalization():
    val, unit = norm.normalize_quantity("500 gms")
    assert val == 500.0
    assert unit == "g"

    val_k, unit_k = norm.normalize_quantity("1.5 kg")
    assert val_k == 1.5
    assert unit_k == "kg"

    mrp_val, curr, tax_inc = norm.normalize_mrp("MRP Rs. 75.50 (Incl. of all taxes)")
    assert mrp_val == 75.50
    assert curr == "INR"
    assert tax_inc is True

    d = norm.normalize_date("05/11/2024")
    assert d == "2024-11-05"

# 3. Test Controlled Category Resolution
def test_category_resolution():
    cats = db.get_all_categories()
    assert len(cats) >= 5
    cat_id, cat_name, conf = ext.resolve_product_category("Organic Peanut Chikki Snack Food Confectionery", cats)
    assert cat_id == "CAT-FOOD"
    assert conf >= 0.75

# 4. Test Versioned Rules Retrieval
def test_versioned_rules_retrieval():
    food_rules = db.get_applicable_rules("CAT-FOOD")
    assert len(food_rules) >= 9
    rule_codes = [r["rule_code"] for r in food_rules]
    assert "LMPC-001" in rule_codes # MRP
    assert "LMPC-003" in rule_codes # Net Qty
    assert "LMPC-004" in rule_codes # USP
    assert "LMPC-006" in rule_codes # Expiry (Food)

# 5. Test Deterministic Compliance Engine on Compliant Package
def test_compliant_package_evaluation():
    p = ProductSchema(
        product_name="Organic Peanut Chikki",
        brand="24 Mantra",
        category_id="CAT-FOOD",
        category_name="Food & Beverages",
        net_quantity=QuantityDeclaration(raw_value="100g", normalized_value=100.0, unit="g", confidence=0.98),
        mrp=PriceDeclaration(raw_value="₹ 50.00 (Incl. of taxes)", normalized_value=50.0, currency="INR", tax_inclusive=True),
        unit_sale_price=UnitSalePriceDeclaration(raw_value="₹ 0.50/g", normalized_value=0.50, unit="Rs/g"),
        manufacture_date=DateDeclaration(raw_value="10/2024", normalized_value="2024-10"),
        expiry_date=DateDeclaration(raw_value="10/2025", normalized_value="2025-10"),
        manufacturer_name="Sresta Natural Bioproducts Ltd, Hyderabad",
        consumer_care=ConsumerCareDeclaration(raw_value="support@sresta.com", email="support@sresta.com"),
        veg_nonveg_status="VEG"
    )
    
    engine = DeterministicComplianceEngine()
    rules = db.get_applicable_rules(p.category_id)
    results = [engine.evaluate_rule(r, p) for r in rules]
    
    failures = [r for r in results if r["status"] == "FAIL"]
    assert len(failures) == 0, f"Expected zero violations, got: {failures}"
    passes = [r for r in results if r["status"] == "PASS"]
    assert len(passes) >= 8

# 6. Test Package with Missing Mandatory MRP (Violation Creation)
def test_missing_mrp_violation():
    p = ProductSchema(
        product_name="Sample Biscuit",
        category_id="CAT-FOOD",
        net_quantity=QuantityDeclaration(raw_value="200g", normalized_value=200.0, unit="g"),
        mrp=PriceDeclaration(), # Missing MRP
        manufacture_date=DateDeclaration(raw_value="01/2025", normalized_value="2025-01"),
        expiry_date=DateDeclaration(raw_value="06/2025", normalized_value="2025-06"),
        manufacturer_name="Sample Foods Pvt Ltd"
    )
    
    engine = DeterministicComplianceEngine()
    rules = db.get_applicable_rules(p.category_id)
    results = [engine.evaluate_rule(r, p) for r in rules]
    
    mrp_res = next((r for r in results if r["rule_code"] == "LMPC-001"), None)
    assert mrp_res is not None
    assert mrp_res["status"] == "FAIL"
    assert "not detected" in mrp_res["reason"].lower()

# 7. Test Non-Standard Unit Violation
def test_non_standard_unit_violation():
    p = ProductSchema(
        product_name="Imported Soap",
        category_id="CAT-ALL",
        net_quantity=QuantityDeclaration(raw_value="12 oz", normalized_value=12.0, unit="oz"), # Non-metric oz
        mrp=PriceDeclaration(raw_value="Rs. 100", normalized_value=100.0),
        manufacture_date=DateDeclaration(raw_value="01/2025", normalized_value="2025-01"),
        manufacturer_name="Global Exports"
    )
    
    engine = DeterministicComplianceEngine()
    rules = db.get_applicable_rules(p.category_id)
    results = [engine.evaluate_rule(r, p) for r in rules]
    
    qty_res = next((r for r in results if r["rule_code"] == "LMPC-003"), None)
    assert qty_res is not None
    assert qty_res["status"] == "FAIL"
    assert "non-standard measurement unit" in qty_res["reason"].lower()

# 8. Test Low Confidence Leads to REVIEW_REQUIRED
def test_low_confidence_review_required():
    p = ProductSchema(
        product_name="Unclear Label Pack",
        category_id="CAT-ALL",
        net_quantity=QuantityDeclaration(raw_value="50g", normalized_value=50.0, unit="g", confidence=0.45), # Low confidence
        mrp=PriceDeclaration(raw_value="Rs 20", normalized_value=20.0),
        manufacture_date=DateDeclaration(raw_value="01/2025", normalized_value="2025-01"),
        manufacturer_name="ABC Foods"
    )
    
    engine = DeterministicComplianceEngine()
    rules = db.get_applicable_rules(p.category_id)
    results = [engine.evaluate_rule(r, p) for r in rules]
    
    qty_res = next((r for r in results if r["rule_code"] == "LMPC-003"), None)
    assert qty_res is not None
    assert qty_res["status"] == "REVIEW_REQUIRED"
    assert qty_res["review_status"] == "UNCERTAIN"

# 9. Complete End-to-End Persistence Pipeline Test
def test_end_to_end_persistence():
    insp_id = "TEST-INSP-001"
    
    # A. Create inspection
    db.create_inspection({
        "id": insp_id,
        "product_name": "Test FMCG Pack",
        "brand": "TestBrand",
        "category_id": "CAT-FOOD",
        "officer_id": "OFFICER-TEST",
        "location": "Zonal Lab"
    })
    
    # B. Insert Image Record
    img_id = "IMG-TEST-01"
    db.save_image_record({
        "id": img_id,
        "inspection_id": insp_id,
        "image_url": "/uploads/test.jpg",
        "file_path": "n:/PROJECTS/INSIST/sih26034/backend/sample_images/sample_front_clear.jpg",
        "view_type": "Front Panel",
        "quality_status": "PASS",
        "quality_score": 0.96,
        "blur_metric": 600.0,
        "brightness_metric": 130.0
    })
    
    # C. Save Raw OCR Tokens
    db.save_ocr_result({
        "id": f"OCR-{img_id}",
        "inspection_id": insp_id,
        "image_id": img_id,
        "raw_text": "Net Wt: 250g MRP Rs. 50.00 Mfg 10/2024 Exp 10/2025",
        "tokens": [{"text": "250g", "confidence": 0.98, "bbox": [10, 20, 30, 40]}],
        "mean_confidence": 0.98
    })
    
    # D. Save Structured Product Data
    p = ProductSchema(
        product_name="Test FMCG Pack",
        brand="TestBrand",
        category_id="CAT-FOOD",
        net_quantity=QuantityDeclaration(raw_value="250g", normalized_value=250.0, unit="g"),
        mrp=PriceDeclaration(raw_value="Rs. 50.00", normalized_value=50.0),
        manufacture_date=DateDeclaration(raw_value="10/2024", normalized_value="2024-10"),
        expiry_date=DateDeclaration(raw_value="10/2025", normalized_value="2025-10"),
        manufacturer_name="Test Industries Ltd"
    )
    db.save_structured_product_data(insp_id, p.model_dump())
    
    # E. Evaluate Rules & Save Violations
    rules = db.get_applicable_rules(p.category_id)
    engine = DeterministicComplianceEngine()
    results = [engine.evaluate_rule(r, p) for r in rules]
    db.save_compliance_violations(insp_id, results)
    
    # F. Retrieve and verify complete inspection record
    insp = db.get_inspection(insp_id)
    assert insp is not None
    assert insp["product_name"] == "Test FMCG Pack"
    
    ocr_res = db.get_ocr_results(insp_id)
    assert len(ocr_res) == 1
    assert "250g" in ocr_res[0]["raw_text"]
    
    spd = db.get_structured_product_data(insp_id)
    assert spd is not None
    assert spd["net_quantity_value"] == 250.0
    
    violations = db.get_compliance_violations(insp_id)
    assert len(violations) >= 8
    print("End-to-End data survival verified across all relational and JSON entities!")

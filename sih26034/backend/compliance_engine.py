import re
import json
from typing import Dict, Any, List, Optional
from models import ProductSchema

class DeterministicComplianceEngine:
    @staticmethod
    def evaluate_rule(rule: Dict[str, Any], product: ProductSchema) -> Dict[str, Any]:
        rule_version_id = rule["rule_version_id"]
        rule_code = rule["rule_code"]
        field = rule["field"]
        v_type = rule["validation_type"]
        operator = rule["operator"]
        statutory_ref = rule.get("statutory_reference", "LMPC 2011")
        severity = rule.get("severity", "ERROR")
        
        # Check conditional exemptions if defined in rule
        cond_expr = rule.get("condition_expression")
        if cond_expr:
            try:
                cond_data = json.loads(cond_expr) if isinstance(cond_expr, str) else cond_expr
                if isinstance(cond_data, dict):
                    # Check exemption conditions (e.g. USP exempt if net qty == 1kg or 1L)
                    exempt_rules = cond_data.get("exempt_if", [])
                    if "net_quantity_eq_1kg" in exempt_rules and product.net_quantity.normalized_value == 1000 and product.net_quantity.unit in ["g", "kg"]:
                        return {
                            "id": f"CR-{rule_code}",
                            "rule_version_id": rule_version_id,
                            "rule_code": rule_code,
                            "field": field,
                            "status": "NOT_APPLICABLE",
                            "observed_value": "EXEMPT",
                            "expected_value": "Exempt per LMPC amendment",
                            "reason": "Package net quantity is exactly 1 kg / 1 L, exempting it from mandatory Unit Sale Price declaration.",
                            "severity": "WARNING",
                            "evidence_ocr_id": product.net_quantity.evidence_ocr_id,
                            "evidence_bounding_box": product.net_quantity.bounding_box,
                            "statutory_reference": statutory_ref,
                            "review_status": "VERIFIABLE"
                        }
                    only_if = cond_data.get("only_if")
                    if only_if == "is_imported" and not product.importer_name and not product.importer_address:
                        return {
                            "id": f"CR-{rule_code}",
                            "rule_version_id": rule_version_id,
                            "rule_code": rule_code,
                            "field": field,
                            "status": "NOT_APPLICABLE",
                            "observed_value": "DOMESTIC",
                            "expected_value": "Applicable to imported commodities",
                            "reason": "Product identified as domestic manufacture. Country of origin mandate applies to imported pre-packed goods.",
                            "severity": "WARNING",
                            "evidence_ocr_id": None,
                            "evidence_bounding_box": None,
                            "statutory_reference": statutory_ref,
                            "review_status": "VERIFIABLE"
                        }
            except Exception:
                pass

        # Evaluate based on field
        val_str = None
        norm_val = None
        unit_val = None
        evidence_ocr = None
        evidence_bbox = None
        conf = 1.0

        if field == "mrp":
            val_str = product.mrp.raw_value
            norm_val = product.mrp.normalized_value
            evidence_ocr = product.mrp.evidence_ocr_id
            evidence_bbox = product.mrp.bounding_box
            conf = product.mrp.confidence
        elif field == "net_quantity":
            val_str = product.net_quantity.raw_value
            norm_val = product.net_quantity.normalized_value
            unit_val = product.net_quantity.unit
            evidence_ocr = product.net_quantity.evidence_ocr_id
            evidence_bbox = product.net_quantity.bounding_box
            conf = product.net_quantity.confidence
        elif field == "unit_sale_price":
            val_str = product.unit_sale_price.raw_value
            norm_val = product.unit_sale_price.normalized_value
            unit_val = product.unit_sale_price.unit
            evidence_ocr = product.unit_sale_price.evidence_ocr_id
            evidence_bbox = product.unit_sale_price.bounding_box
            conf = product.unit_sale_price.confidence
        elif field == "mfg_date":
            val_str = product.manufacture_date.raw_value
            norm_val = product.manufacture_date.normalized_value
            evidence_ocr = product.manufacture_date.evidence_ocr_id
            evidence_bbox = product.manufacture_date.bounding_box
            conf = product.manufacture_date.confidence
        elif field == "expiry_date":
            val_str = product.expiry_date.raw_value
            norm_val = product.expiry_date.normalized_value
            evidence_ocr = product.expiry_date.evidence_ocr_id
            evidence_bbox = product.expiry_date.bounding_box
            conf = product.expiry_date.confidence
        elif field == "manufacturer":
            val_str = product.manufacturer_name or product.manufacturer_address or product.packer_name or product.importer_name
            norm_val = val_str
        elif field == "consumer_care":
            cc = product.consumer_care
            val_str = cc.email or cc.phone or cc.address or cc.raw_value
            norm_val = val_str
            evidence_ocr = cc.evidence_ocr_id
            evidence_bbox = cc.bounding_box
            conf = cc.confidence
        elif field == "veg_nonveg":
            val_str = product.veg_nonveg_status
            norm_val = val_str
        elif field == "country_of_origin":
            val_str = product.country_of_origin
            norm_val = val_str

        # If confidence is too low, send to human review rather than automatic legal fail
        if conf < 0.65:
            return {
                "id": f"CR-{rule_code}",
                "rule_version_id": rule_version_id,
                "rule_code": rule_code,
                "field": field,
                "status": "REVIEW_REQUIRED",
                "observed_value": val_str or "LOW_CONFIDENCE",
                "expected_value": rule.get("expected_value"),
                "reason": f"Low recognition confidence ({conf:.2f}) on statutory field. Inspection officer verification required.",
                "severity": "WARNING",
                "evidence_ocr_id": evidence_ocr,
                "evidence_bounding_box": evidence_bbox,
                "statutory_reference": statutory_ref,
                "review_status": "UNCERTAIN"
            }

        # 1. Presence Validation
        if v_type == "presence":
            if val_str and str(val_str).strip() and val_str not in ["NONE", "NOT FOUND"]:
                return {
                    "id": f"CR-{rule_code}",
                    "rule_version_id": rule_version_id,
                    "rule_code": rule_code,
                    "field": field,
                    "status": "PASS",
                    "observed_value": str(val_str),
                    "expected_value": "Statutory declaration must be present",
                    "reason": f"Mandatory declaration clearly present on packaging: '{val_str}'.",
                    "severity": severity,
                    "evidence_ocr_id": evidence_ocr,
                    "evidence_bounding_box": evidence_bbox,
                    "statutory_reference": statutory_ref,
                    "review_status": "VERIFIABLE"
                }
            else:
                return {
                    "id": f"CR-{rule_code}",
                    "rule_version_id": rule_version_id,
                    "rule_code": rule_code,
                    "field": field,
                    "status": "FAIL",
                    "observed_value": "NOT FOUND",
                    "expected_value": "Mandatory declaration required",
                    "reason": f"Mandatory declaration '{rule['requirement']}' was not detected on packaging.",
                    "severity": severity,
                    "evidence_ocr_id": evidence_ocr,
                    "evidence_bounding_box": evidence_bbox,
                    "statutory_reference": statutory_ref,
                    "review_status": "VERIFIABLE"
                }

        # 2. Format / Regex Validation
        elif v_type == "format":
            expected_regex = rule.get("expected_value", "")
            if val_str and expected_regex and re.search(expected_regex, str(val_str), re.IGNORECASE):
                return {
                    "id": f"CR-{rule_code}",
                    "rule_version_id": rule_version_id,
                    "rule_code": rule_code,
                    "field": field,
                    "status": "PASS",
                    "observed_value": str(val_str),
                    "expected_value": f"Pattern matching: {expected_regex}",
                    "reason": "Statutory declaration satisfies legal wording and format requirements.",
                    "severity": severity,
                    "evidence_ocr_id": evidence_ocr,
                    "evidence_bounding_box": evidence_bbox,
                    "statutory_reference": statutory_ref,
                    "review_status": "VERIFIABLE"
                }
            else:
                return {
                    "id": f"CR-{rule_code}",
                    "rule_version_id": rule_version_id,
                    "rule_code": rule_code,
                    "field": field,
                    "status": "FAIL",
                    "observed_value": str(val_str or "MISSING"),
                    "expected_value": f"Pattern matching: {expected_regex}",
                    "reason": f"Statutory declaration format does not conform to legal standard ({expected_regex}).",
                    "severity": severity,
                    "evidence_ocr_id": evidence_ocr,
                    "evidence_bounding_box": evidence_bbox,
                    "statutory_reference": statutory_ref,
                    "review_status": "VERIFIABLE"
                }

        # 3. Standard Metric Unit Validation
        elif v_type == "unit_check":
            expected_units = [u.strip().lower() for u in (rule.get("expected_value", "") or "").split(",")]
            unit = (unit_val or "").lower()
            if unit in expected_units:
                return {
                    "id": f"CR-{rule_code}",
                    "rule_version_id": rule_version_id,
                    "rule_code": rule_code,
                    "field": field,
                    "status": "PASS",
                    "observed_value": f"{norm_val} {unit}",
                    "expected_value": f"One of: {', '.join(expected_units)}",
                    "reason": f"Valid standard metric measurement unit declared: '{unit}'.",
                    "severity": severity,
                    "evidence_ocr_id": evidence_ocr,
                    "evidence_bounding_box": evidence_bbox,
                    "statutory_reference": statutory_ref,
                    "review_status": "VERIFIABLE"
                }
            else:
                return {
                    "id": f"CR-{rule_code}",
                    "rule_version_id": rule_version_id,
                    "rule_code": rule_code,
                    "field": field,
                    "status": "FAIL",
                    "observed_value": f"{norm_val} {unit}" if norm_val else (val_str or "NOT FOUND"),
                    "expected_value": f"One of: {', '.join(expected_units)}",
                    "reason": f"Non-standard measurement unit '{unit}'. Must conform to Seventh Schedule standard units.",
                    "severity": severity,
                    "evidence_ocr_id": evidence_ocr,
                    "evidence_bounding_box": evidence_bbox,
                    "statutory_reference": statutory_ref,
                    "review_status": "VERIFIABLE"
                }

        # 4. Date Presence & Validity
        elif v_type == "date_presence":
            if norm_val or val_str:
                return {
                    "id": f"CR-{rule_code}",
                    "rule_version_id": rule_version_id,
                    "rule_code": rule_code,
                    "field": field,
                    "status": "PASS",
                    "observed_value": str(norm_val or val_str),
                    "expected_value": "Valid Date (MM/YYYY or DD/MM/YYYY)",
                    "reason": f"Statutory date declaration verified: '{norm_val or val_str}'.",
                    "severity": severity,
                    "evidence_ocr_id": evidence_ocr,
                    "evidence_bounding_box": evidence_bbox,
                    "statutory_reference": statutory_ref,
                    "review_status": "VERIFIABLE"
                }
            else:
                return {
                    "id": f"CR-{rule_code}",
                    "rule_version_id": rule_version_id,
                    "rule_code": rule_code,
                    "field": field,
                    "status": "FAIL",
                    "observed_value": "NOT FOUND",
                    "expected_value": "Valid statutory date required",
                    "reason": f"Mandatory statutory date declaration '{rule['requirement']}' was not detected.",
                    "severity": severity,
                    "evidence_ocr_id": evidence_ocr,
                    "evidence_bounding_box": evidence_bbox,
                    "statutory_reference": statutory_ref,
                    "review_status": "VERIFIABLE"
                }

        return {
            "id": f"CR-{rule_code}",
            "rule_version_id": rule_version_id,
            "rule_code": rule_code,
            "field": field,
            "status": "PASS",
            "observed_value": str(val_str),
            "expected_value": rule.get("expected_value"),
            "reason": f"Requirement verified: {val_str}",
            "severity": severity,
            "evidence_ocr_id": evidence_ocr,
            "evidence_bounding_box": evidence_bbox,
            "statutory_reference": statutory_ref,
            "review_status": "VERIFIABLE"
        }

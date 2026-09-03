import unittest
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, r"n:\PROJECTS\INSIST\sih26034\backend")

from compliance_engine import DeterministicComplianceEngine
import exceptions as exc
import review_logic as rl
import database as db

class TestComplianceEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()
        cls.engine = DeterministicComplianceEngine()

    def test_01_required_field_present(self):
        rule = {
            "rule_id": "LMPC-001",
            "field": "mrp",
            "requirement": "MRP Declaration",
            "validation_type": "presence",
            "operator": "exists"
        }
        facts = [{
            "id": "F-1",
            "field_name": "mrp",
            "value": "MRP Rs. 50.00 (Incl. of all taxes)",
            "confidence": 0.96,
            "extraction_status": "FOUND"
        }]
        res = self.engine.evaluate_rule(rule, facts, {})
        self.assertEqual(res["status"], "PASS")
        suff = rl.determine_evidence_sufficiency(res, facts)
        self.assertEqual(suff, "VERIFIABLE")

    def test_02_required_field_absent(self):
        rule = {
            "rule_id": "LMPC-001",
            "field": "mrp",
            "requirement": "MRP Declaration",
            "validation_type": "presence",
            "operator": "exists"
        }
        facts = []
        res = self.engine.evaluate_rule(rule, facts, {})
        self.assertEqual(res["status"], "FAIL")
        self.assertEqual(res["observed_value"], "NOT FOUND")

    def test_03_field_unreadable(self):
        rule = {
            "rule_id": "LMPC-001",
            "field": "mrp",
            "requirement": "MRP Declaration",
            "validation_type": "presence",
            "operator": "exists"
        }
        facts = [{
            "id": "F-2",
            "field_name": "mrp",
            "value": "M.R.? ..50",
            "confidence": 0.35,
            "extraction_status": "UNREADABLE"
        }]
        res = self.engine.evaluate_rule(rule, facts, {})
        self.assertEqual(res["status"], "UNCERTAIN")
        suff = rl.determine_evidence_sufficiency(res, facts)
        self.assertEqual(suff, "UNCERTAIN")

    def test_04_low_confidence_routes_to_uncertain(self):
        rule = {
            "rule_id": "LMPC-001",
            "field": "mrp",
            "requirement": "MRP Declaration",
            "validation_type": "presence",
            "operator": "exists"
        }
        facts = [{
            "id": "F-3",
            "field_name": "mrp",
            "value": "Rs 50",
            "confidence": 0.52,  # < 0.60
            "extraction_status": "FOUND"
        }]
        res = self.engine.evaluate_rule(rule, facts, {})
        self.assertEqual(res["status"], "PASS")
        suff = rl.determine_evidence_sufficiency(res, facts)
        self.assertEqual(suff, "UNCERTAIN")  # Low confidence routes to review!

    def test_05_conflicting_values_across_images(self):
        rule = {
            "rule_id": "LMPC-001",
            "field": "mrp",
            "requirement": "MRP Declaration",
            "validation_type": "presence",
            "operator": "exists"
        }
        facts = [
            {"id": "F-Front", "field_name": "mrp", "value": "MRP Rs. 50", "confidence": 0.95, "extraction_status": "FOUND"},
            {"id": "F-Back", "field_name": "mrp", "value": "MRP Rs. 60", "confidence": 0.95, "extraction_status": "FOUND"}
        ]
        res = self.engine.evaluate_rule(rule, facts, {})
        self.assertEqual(res["status"], "CONFLICT")
        suff = rl.determine_evidence_sufficiency(res, facts)
        self.assertEqual(suff, "UNCERTAIN")

    def test_06_unit_validation(self):
        rule = {
            "rule_id": "LMPC-003",
            "field": "net_quantity",
            "requirement": "Standard Metric Units",
            "validation_type": "unit_check",
            "operator": "in_list",
            "expected_value": "g,kg,ml,l,m,cm,mm,units,pcs"
        }
        valid_fact = [{"id": "F-4", "field_name": "net_quantity", "value": "250 g", "unit": "g", "confidence": 0.95, "extraction_status": "FOUND"}]
        res_pass = self.engine.evaluate_rule(rule, valid_fact, {})
        self.assertEqual(res_pass["status"], "PASS")

        invalid_fact = [{"id": "F-5", "field_name": "net_quantity", "value": "10 ounces", "unit": "oz", "confidence": 0.95, "extraction_status": "FOUND"}]
        res_fail = self.engine.evaluate_rule(rule, invalid_fact, {})
        self.assertEqual(res_fail["status"], "FAIL")

    def test_07_rule_exemption_non_food(self):
        rule = {
            "rule_id": "LMPC-010",
            "category": "Food",
            "field": "veg_nonveg",
            "requirement": "Veg Logo"
        }
        ex_check = exc.check_rule_exemptions(rule, {}, "Electronics")
        self.assertFalse(ex_check["applicable"])

if __name__ == "__main__":
    unittest.main()

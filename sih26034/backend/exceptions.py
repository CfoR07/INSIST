from typing import Dict, Any

def check_rule_exemptions(rule: Dict[str, Any], facts_by_field: Dict[str, Any], category: str) -> Dict[str, Any]:
    rule_id = rule.get("rule_id", "")
    rule_cat = rule.get("category", "ALL")
    
    if rule_cat != "ALL" and rule_cat.lower() != category.lower():
        return {
            "applicable": False,
            "exemption_reason": f"Rule applies only to '{rule_cat}', but product category is '{category}'."
        }
        
    net_qty_fact_list = facts_by_field.get("net_quantity", [])
    if net_qty_fact_list:
        net_qty_fact = net_qty_fact_list[0]
        norm_val = net_qty_fact.get("normalized_value")
        unit = str(net_qty_fact.get("unit", "")).lower()
        try:
            val_float = float(norm_val) if norm_val else None
            if val_float is not None and val_float <= 10.0 and unit in ["g", "gm", "ml"]:
                if rule_id in ["LMPC-004", "LMPC-008"]:
                    return {
                        "applicable": False,
                        "exemption_reason": f"Exempt under Rule 26: Small package ({val_float}{unit} <= 10{unit})."
                    }
        except Exception:
            pass
            
    if rule_id == "LMPC-004" and net_qty_fact_list:
        net_qty_fact = net_qty_fact_list[0]
        norm_val = net_qty_fact.get("normalized_value")
        unit = str(net_qty_fact.get("unit", "")).lower()
        try:
            val_float = float(norm_val) if norm_val else None
            if val_float == 1.0 and unit in ["kg", "l", "litre", "liter"]:
                return {
                    "applicable": False,
                    "exemption_reason": "Unit Sale Price declaration not required when package is exactly 1 kg / 1 L."
                }
        except Exception:
            pass

    return {"applicable": True, "exemption_reason": None}

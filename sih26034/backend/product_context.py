from typing import Dict, Any

FOOD_KEYWORDS = ['biscuit', 'cookie', 'bread', 'cake', 'snack', 'chips', 'namkeen', 'chocolate', 'flour', 'atta', 'rice', 'spice', 'masala', 'oil', 'ghee', 'milk', 'tea', 'coffee', 'juice', 'sugar', 'salt', 'sauce', 'ketchup', 'pasta', 'noodle']
COSMETICS_KEYWORDS = ['shampoo', 'soap', 'cream', 'lotion', 'serum', 'oil', 'perfume', 'deodorant', 'lipstick', 'face wash', 'powder', 'gel', 'sunscreen']
ELECTRONICS_KEYWORDS = ['cable', 'charger', 'bulb', 'led', 'battery', 'adapter', 'mouse', 'keyboard', 'earphone', 'headphone']

def infer_product_context(extracted_text_corpus: str, detected_product_name: str = '') -> Dict[str, Any]:
    combined = (extracted_text_corpus + ' ' + detected_product_name).lower()
    food_score = sum(1 for kw in FOOD_KEYWORDS if kw in combined)
    cosmetic_score = sum(1 for kw in COSMETICS_KEYWORDS if kw in combined)
    elec_score = sum(1 for kw in ELECTRONICS_KEYWORDS if kw in combined)
    
    if food_score == 0 and cosmetic_score == 0 and elec_score == 0:
        category = 'General Commodity'
        confidence = 0.85
    elif food_score >= cosmetic_score and food_score >= elec_score:
        category = 'Food'
        confidence = round(min(0.98, 0.70 + (food_score * 0.08)), 2)
    elif cosmetic_score >= elec_score:
        category = 'Cosmetics'
        confidence = round(min(0.98, 0.70 + (cosmetic_score * 0.08)), 2)
    else:
        category = 'Electronics'
        confidence = round(min(0.98, 0.70 + (elec_score * 0.08)), 2)
        
    return {
        'inferred_category': category,
        'confidence': confidence,
        'requires_officer_confirmation': confidence < 0.75
    }

import os
import re
from typing import Dict, Any, List
import fitz # PyMuPDF
from bs4 import BeautifulSoup

def extract_document_text(file_path: str) -> str:
    if not os.path.exists(file_path):
        return ""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        try:
            doc = fitz.open(file_path)
            pages_text = []
            for page in doc:
                pages_text.append(page.get_text())
            return "\n".join(pages_text)
        except Exception:
            pass
            
    # HTML / Text fallback
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            soup = BeautifulSoup(content, "html.parser")
            return soup.get_text()
    except Exception:
        return ""

def parse_metadata_and_clauses(text: str) -> Dict[str, Any]:
    clauses = []
    
    # 1. Match Notification Number
    notif_match = re.search(r'(?:G\.S\.R\.?\s*[0-9]+(?:\([A-Za-z]+\))?|F\.\s*No\.[A-Za-z0-9/_-]+)', text, re.IGNORECASE)
    notification_no = notif_match.group(0).strip() if notif_match else None
    
    # 2. Extract Rule Numbers & Sub-rules
    rule_matches = re.finditer(r'(?:Rule|rule|sub-rule|clause)\s*([0-9]+(?:\([0-9a-zA-Z]+\))*)', text)
    for m in rule_matches:
        r_str = m.group(0)
        if r_str not in clauses:
            clauses.append(r_str)
            
    # 3. Detect Amendment Actions
    amendment_actions = []
    if re.search(r'(?:substituted|shall be substituted)', text, re.IGNORECASE):
        amendment_actions.append("SUBSTITUTION")
    if re.search(r'(?:inserted|shall be inserted)', text, re.IGNORECASE):
        amendment_actions.append("INSERTION")
    if re.search(r'(?:omitted|shall be omitted)', text, re.IGNORECASE):
        amendment_actions.append("OMISSION")
        
    return {
        "notification_number": notification_no,
        "referenced_clauses": clauses[:15],
        "amendment_actions": amendment_actions,
        "char_count": len(text)
    }

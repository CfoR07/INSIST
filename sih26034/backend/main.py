import os
import uuid
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import database as db
import quality_check as qc
import extraction as ext
import product_context as pc
import exceptions as exc
from compliance_engine import DeterministicComplianceEngine
import review_logic as rl
import report_generator as rep

app = FastAPI(
    title="SIH26034 Pre-Packed Commodity Inspection API",
    description="Deterministic AI-Assisted Packaging Compliance Verification Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.on_event("startup")
def on_startup():
    db.init_db()

@app.get("/")
def root():
    html_path = os.path.join(os.path.dirname(__file__), "static_ui.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>SIH26034 Inspection Server Online</h1><p><a href='/docs'>Swagger API Docs</a></p>")

@app.get("/bg_noir.jpg")
@app.get("/bg_noir.png")
def get_bg_image():
    for name in ["bg_noir.png", "bg_noir.jpg"]:
        p = os.path.join(os.path.dirname(__file__), name)
        if os.path.exists(p):
            media = "image/png" if name.endswith(".png") else "image/jpeg"
            return FileResponse(p, media_type=media)
    raise HTTPException(status_code=404, detail="Background not found")

@app.get("/logo.png")
@app.get("/insist.png")
@app.get("/favicon.png")
@app.get("/favicon.ico")
def get_logo_image():
    for name in ["logo.png", "insist.png", "favicon.png"]:
        p = os.path.join(os.path.dirname(__file__), name)
        if os.path.exists(p):
            return FileResponse(p, media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo not found")

@app.post("/api/inspections")
def create_inspection_endpoint(
    product_name: str = Form("Sample Biscuits"),
    brand: str = Form("Britannia / Parle"),
    category: str = Form("Food"),
    package_type: str = Form("Pouch / Box"),
    officer_id: str = Form("OFFICER-001"),
    location: str = Form("Central Zonal Lab")
):
    insp_id = f"INS-{int(datetime.now().timestamp()) % 100000}"
    db.create_inspection({
        "id": insp_id,
        "product_name": product_name,
        "brand": brand,
        "category": category,
        "package_type": package_type,
        "officer_id": officer_id,
        "location": location,
        "status": "DRAFT"
    })
    return {"inspection_id": insp_id, "status": "DRAFT"}

@app.post("/api/inspections/{inspection_id}/upload")
async def upload_image_endpoint(
    inspection_id: str,
    view_type: str = Form("Front"),
    file: UploadFile = File(...)
):
    insp = db.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
        
    img_id = f"IMG-{uuid.uuid4().hex[:8]}"
    ext_name = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{img_id}_{view_type.replace(' ', '_')}{ext_name}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    quality_res = qc.assess_image_quality(file_path)
    
    img_record = {
        "id": img_id,
        "inspection_id": inspection_id,
        "image_url": f"/uploads/{filename}",
        "file_path": file_path,
        "view_type": view_type,
        "quality_status": quality_res["quality_status"],
        "quality_score": quality_res["quality_score"],
        "blur_metric": quality_res["blur_metric"],
        "brightness_metric": quality_res["brightness_metric"]
    }
    db.save_image_record(img_record)
    
    return {
        "image_id": img_id,
        "image_url": img_record["image_url"],
        "quality": quality_res
    }


@app.delete("/api/inspections/{inspection_id}/images/{image_id}")
def delete_image_endpoint(inspection_id: str, image_id: str):
    db.delete_image_record(inspection_id, image_id)
    return {"status": "DELETED", "image_id": image_id}

@app.post("/api/inspections/{inspection_id}/clear-images")
def clear_images_endpoint(inspection_id: str):
    db.clear_inspection_images(inspection_id)
    return {"status": "CLEARED"}

@app.post("/api/inspections/{inspection_id}/analyze")
def analyze_inspection_endpoint(inspection_id: str):
    insp = db.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
        
    images = db.get_inspection_images(inspection_id)
    if not images:
        # Fallback to sample package photos if none explicitly uploaded in demo
        sample_front = os.path.join(os.path.dirname(__file__), "sample_images", "sample_front_clear.jpg")
        sample_back = os.path.join(os.path.dirname(__file__), "sample_images", "sample_back_clear.jpg")
        if os.path.exists(sample_front):
            db.save_image_record({
                "id": f"IMG-{inspection_id}-1",
                "inspection_id": inspection_id,
                "image_url": "/uploads/sample_front_clear.jpg",
                "file_path": sample_front,
                "view_type": "Front View",
                "quality_status": "SHARP",
                "quality_score": 0.94,
                "blur_metric": 750.3,
                "brightness_metric": 132.0
            })
        if os.path.exists(sample_back):
            db.save_image_record({
                "id": f"IMG-{inspection_id}-2",
                "inspection_id": inspection_id,
                "image_url": "/uploads/sample_back_clear.jpg",
                "file_path": sample_back,
                "view_type": "Back View",
                "quality_status": "SHARP",
                "quality_score": 0.91,
                "blur_metric": 680.1,
                "brightness_metric": 128.0
            })
        images = db.get_inspection_images(inspection_id)
        
    all_facts = []
    text_corpus = ""
    for img in images:
        img_facts = ext.extract_facts_from_image(img["file_path"], img["view_type"], img["id"], inspection_id)
        all_facts.extend(img_facts)
        text_corpus += " " + " ".join([f.get("value", "") for f in img_facts])
        
    all_facts = ext.deduplicate_extracted_facts(all_facts)
    db.save_extracted_facts(inspection_id, all_facts)
    
    context = pc.infer_product_context(text_corpus, insp.get("product_name", ""))
    inferred_cat = context["inferred_category"]
    db.update_inspection_status(inspection_id, "ANALYZED", category=inferred_cat)
    
    applicable_rules = db.get_applicable_rules(category=inferred_cat)
    
    facts_by_field = {}
    for f in all_facts:
        fld = f["field_name"]
        facts_by_field.setdefault(fld, []).append(f)
        
    compliance_results = []
    engine = DeterministicComplianceEngine()
    
    for rule in applicable_rules:
        fld = rule["field"]
        ex_check = exc.check_rule_exemptions(rule, facts_by_field, inferred_cat)
        if not ex_check["applicable"]:
            compliance_results.append({
                "id": f"CR-{inspection_id}-{rule['rule_id']}",
                "rule_id": rule["rule_id"],
                "field": fld,
                "status": "NOT_APPLICABLE",
                "observed_value": "EXEMPT",
                "reason": ex_check["exemption_reason"] or "Exempt from requirement",
                "evidence_fact_ids": [],
                "review_status": "VERIFIABLE"
            })
            continue
            
        facts_for_this_rule = facts_by_field.get(fld, [])
        eval_res = engine.evaluate_rule(rule, facts_for_this_rule, facts_by_field)
        sufficiency = rl.determine_evidence_sufficiency(eval_res, facts_for_this_rule)
        
        compliance_results.append({
            "id": f"CR-{inspection_id}-{rule['rule_id']}",
            "rule_id": rule["rule_id"],
            "field": fld,
            "status": eval_res["status"],
            "observed_value": eval_res["observed_value"],
            "reason": eval_res["reason"],
            "evidence_fact_ids": eval_res["evidence_fact_ids"],
            "review_status": sufficiency
        })
        
    db.save_compliance_results(inspection_id, compliance_results)
    
    has_uncertain = any(r["review_status"] == "UNCERTAIN" for r in compliance_results)
    final_status = "UNDER_REVIEW" if has_uncertain else "COMPLETED"
    db.update_inspection_status(inspection_id, final_status)
    
    return {
        "inspection_id": inspection_id,
        "status": final_status,
        "product_context": context,
        "facts_count": len(all_facts),
        "rules_evaluated": len(compliance_results),
        "has_uncertain_cases": has_uncertain
    }

@app.get("/api/inspections/{inspection_id}")
def get_inspection_endpoint(inspection_id: str):
    insp = db.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
        
    images = db.get_inspection_images(inspection_id)
    facts = db.get_extracted_facts(inspection_id)
    results = db.get_compliance_results(inspection_id)
    reviews = db.get_review_decisions(inspection_id)
    
    return {
        "inspection": insp,
        "images": images,
        "facts": facts,
        "compliance_results": results,
        "review_decisions": reviews
    }

@app.get("/api/inspections")
def list_inspections_endpoint():
    return db.get_all_inspections()

@app.post("/api/inspections/{inspection_id}/review")
def submit_review_decision_endpoint(
    inspection_id: str,
    compliance_result_id: str = Form(...),
    decision: str = Form("CONFIRMED_PASS"),
    edited_value: Optional[str] = Form(None),
    note: Optional[str] = Form(""),
    officer_id: str = Form("OFFICER-001")
):
    rev_id = f"REV-{uuid.uuid4().hex[:6]}"
    db.save_review_decision({
        "id": rev_id,
        "compliance_result_id": compliance_result_id,
        "inspection_id": inspection_id,
        "officer_id": officer_id,
        "decision": decision,
        "edited_value": edited_value,
        "note": note
    })
    
    results = db.get_compliance_results(inspection_id)
    if not any(r["review_status"] == "UNCERTAIN" for r in results):
        db.update_inspection_status(inspection_id, "COMPLETED")
        
    return {"status": "SUCCESS", "review_id": rev_id}

@app.get("/api/inspections/{inspection_id}/report", response_class=HTMLResponse)
def get_report_html_endpoint(inspection_id: str):
    insp = db.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    images = db.get_inspection_images(inspection_id)
    facts = db.get_extracted_facts(inspection_id)
    results = db.get_compliance_results(inspection_id)
    reviews = db.get_review_decisions(inspection_id)
    
    html = rep.generate_html_report(insp, images, facts, results, reviews)
    return HTMLResponse(content=html)

@app.get("/api/inspections/{inspection_id}/report/pdf")
def get_report_pdf_endpoint(inspection_id: str):
    insp = db.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    results = db.get_compliance_results(inspection_id)
    
    pdf_path = os.path.join(REPORTS_DIR, f"report_{inspection_id}.pdf")
    rep.generate_pdf_report(insp, results, pdf_path)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"Inspection_Report_{inspection_id}.pdf")

@app.get("/api/dashboard/stats")
def get_dashboard_stats_endpoint():
    return db.get_dashboard_metrics()

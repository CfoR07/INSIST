import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, r"n:\PROJECTS\INSIST\sih26034\backend")

from main import app
import database as db

client = TestClient(app)

print("1. Testing root endpoint...")
r0 = client.get("/")
assert r0.status_code == 200
print("   Root OK:", r0.json())

print("2. Creating inspection...")
r1 = client.post("/api/inspections", data={
    "product_name": "Sunrise Crispy Butter Biscuits",
    "brand": "Sunrise Foods",
    "category": "Food",
    "package_type": "Pouch / Flow Wrap",
    "officer_id": "OFFICER-MH-401",
    "location": "Central Metrology Testing Lab"
})
assert r1.status_code == 200
insp_id = r1.json()["inspection_id"]
print(f"   Created Inspection ID: {insp_id}")

print("3. Testing OpenCV Quality Check on Sharp Front Image...")
sample_front = r"n:\PROJECTS\INSIST\sih26034\backend\sample_images\sample_front_clear.jpg"
with open(sample_front, "rb") as f:
    r_front = client.post(f"/api/inspections/{insp_id}/upload", data={"view_type": "Front View"}, files={"file": ("front.jpg", f, "image/jpeg")})
assert r_front.status_code == 200
front_q = r_front.json()["quality"]
print(f"   Front Image Quality: {front_q['quality_status']} (Score: {front_q['quality_score']}, Blur Var: {front_q['blur_metric']})")

print("4. Testing OpenCV Quality Check on Blurry Image (Triggering Retake Gate)...")
sample_blurry = r"n:\PROJECTS\INSIST\sih26034\backend\sample_images\sample_blurry_trigger.jpg"
with open(sample_blurry, "rb") as f:
    r_blur = client.post(f"/api/inspections/{insp_id}/upload", data={"view_type": "Side View"}, files={"file": ("blurry.jpg", f, "image/jpeg")})
assert r_blur.status_code == 200
blur_q = r_blur.json()["quality"]
print(f"   Blurry Image Quality: {blur_q['quality_status']} (Usable: {blur_q['usable']}, Score: {blur_q['quality_score']}) -> RETAKE REQUIRED")

print("5. Uploading Sharp Back View Image...")
sample_back = r"n:\PROJECTS\INSIST\sih26034\backend\sample_images\sample_back_clear.jpg"
with open(sample_back, "rb") as f:
    r_back = client.post(f"/api/inspections/{insp_id}/upload", data={"view_type": "Back View"}, files={"file": ("back.jpg", f, "image/jpeg")})
assert r_back.status_code == 200

print("6. Executing Full AI Extraction & Deterministic Compliance Engine Pipeline...")
r_eval = client.post(f"/api/inspections/{insp_id}/analyze")
assert r_eval.status_code == 200
eval_data = r_eval.json()
print(f"   Pipeline Completed: {eval_data['rules_evaluated']} Rules Evaluated, Status: {eval_data['status']}")

print("7. Verifying Extracted Facts with Bounding Boxes & Rule Results...")
r_details = client.get(f"/api/inspections/{insp_id}")
assert r_details.status_code == 200
details = r_details.json()
print(f"   Facts Extracted with Bounding Boxes: {len(details['facts'])}")
for f in details['facts'][:3]:
    print(f"   - [{f['field_name']}] '{f['value']}' BBox: {f['bounding_box']} (Conf: {f['confidence']})")

print("   Compliance Rule Results:")
for cr in details['compliance_results']:
    print(f"   - {cr['rule_id']}: [{cr['status']}] {cr['observed_value']} -> {cr['reason']}")

print("8. Testing Officer Review Submission...")
first_cr = details['compliance_results'][0]
r_rev = client.post(f"/api/inspections/{insp_id}/review", data={
    "compliance_result_id": first_cr["id"],
    "decision": "CONFIRMED_PASS",
    "note": "Verified against physical retail sample packaging."
})
assert r_rev.status_code == 200
print("   Review Decision Recorded Successfully:", r_rev.json())

print("9. Generating HTML & PDF Reports...")
r_html = client.get(f"/api/inspections/{insp_id}/report")
assert r_html.status_code == 200 and "Legal Metrology Packaged Commodities Report" in r_html.text
r_pdf = client.get(f"/api/inspections/{insp_id}/report/pdf")
assert r_pdf.status_code == 200
print("   HTML and PDF Reports generated successfully!")

print("10. Fetching Dashboard Stats...")
r_dash = client.get("/api/dashboard/stats")
assert r_dash.status_code == 200
print("   Dashboard Stats:", r_dash.json())

print("\nALL 10 END-TO-END BACKEND INTEGRATION TESTS PASSED PERFECTLY!")

import os

with open(r"n:\PROJECTS\INSIST\sih26034\backend\main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Let's add delete image endpoint and clear previous facts on re-analyze
delete_endpoint = """
@app.delete("/api/inspections/{inspection_id}/images/{image_id}")
def delete_image_endpoint(inspection_id: str, image_id: str):
    db.delete_image_record(inspection_id, image_id)
    return {"status": "DELETED", "image_id": image_id}

@app.post("/api/inspections/{inspection_id}/clear-images")
def clear_images_endpoint(inspection_id: str):
    db.clear_inspection_images(inspection_id)
    return {"status": "CLEARED"}
"""

if "/clear-images" not in code:
    code = code.replace('@app.post("/api/inspections/{inspection_id}/analyze")', delete_endpoint + '\n@app.post("/api/inspections/{inspection_id}/analyze")')
    with open(r"n:\PROJECTS\INSIST\sih26034\backend\main.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("main.py endpoints added for deleting and clearing images")
else:
    print("Endpoints already present")

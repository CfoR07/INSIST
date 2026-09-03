import os

with open(r"n:\PROJECTS\INSIST\sih26034\backend\database.py", "r", encoding="utf-8") as f:
    code = f.read()

db_methods = """
def delete_image_record(inspection_id: str, image_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM inspection_images WHERE id = ? AND inspection_id = ?", (image_id, inspection_id))
    c.execute("DELETE FROM extracted_facts WHERE source_image_id = ? AND inspection_id = ?", (image_id, inspection_id))
    conn.commit()
    conn.close()

def clear_inspection_images(inspection_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM inspection_images WHERE inspection_id = ?", (inspection_id,))
    c.execute("DELETE FROM extracted_facts WHERE inspection_id = ?", (inspection_id,))
    c.execute("DELETE FROM compliance_results WHERE inspection_id = ?", (inspection_id,))
    conn.commit()
    conn.close()
"""

if "def delete_image_record" not in code:
    code += "\n" + db_methods
    with open(r"n:\PROJECTS\INSIST\sih26034\backend\database.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("database.py updated with delete_image_record and clear_inspection_images")
else:
    print("Methods already in database.py")

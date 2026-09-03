import os

with open(r"n:\PROJECTS\INSIST\sih26034\backend\main.py", "r", encoding="utf-8") as f:
    code = f.read()

target = '    db.save_extracted_facts(inspection_id, all_facts)'
replacement = '''    all_facts = ext.deduplicate_extracted_facts(all_facts)
    db.save_extracted_facts(inspection_id, all_facts)'''

code = code.replace(target, replacement, 1)

with open(r"n:\PROJECTS\INSIST\sih26034\backend\main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("main.py deduplication patched cleanly")

import os

with open(r"n:\PROJECTS\INSIST\sih26034\backend\main.py", "r", encoding="utf-8") as f:
    code = f.read()

target = '''    # Save extracted facts to DB
    db.save_extracted_facts(inspection_id, all_facts)'''

replacement = '''    # Deduplicate facts across all packaging views so each field appears EXACTLY ONCE
    deduped_facts = ext.deduplicate_extracted_facts(all_facts)
    db.save_extracted_facts(inspection_id, deduped_facts)
    all_facts = deduped_facts'''

if target in code:
    code = code.replace(target, replacement)
    with open(r"n:\PROJECTS\INSIST\sih26034\backend\main.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("main.py updated with deduplication before database save")
else:
    print("Target already updated")

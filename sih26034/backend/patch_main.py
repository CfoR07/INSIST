import os

with open(r"n:\PROJECTS\INSIST\sih26034\backend\main.py", "r", encoding="utf-8") as f:
    code = f.read()

target = 'def root():\n    return {\n        "system": "SIH26034 Pre-Packed Commodity Inspection Engine",\n        "status": "ONLINE",\n        "philosophy": "AI reads. Code decides."\n    }'

replacement = '''def root():
    html_path = os.path.join(os.path.dirname(__file__), "static_ui.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>SIH26034 Inspection Server Online</h1><p><a href='/docs'>Swagger API Docs</a></p>")'''

if target in code:
    code = code.replace(target, replacement)
    with open(r"n:\PROJECTS\INSIST\sih26034\backend\main.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("main.py root endpoint successfully replaced")
else:
    print("Target not found directly, writing clean endpoint")

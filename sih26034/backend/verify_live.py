import urllib.request
import json
import urllib.parse

data = urllib.parse.urlencode({
    "product_name": "24 Mantra Organic Peanut Chikki",
    "brand": "24 Mantra Organic",
    "category": "Food",
    "officer_id": "INSP-MH-401"
}).encode("utf-8")

req = urllib.request.Request("http://127.0.0.1:8000/api/inspections", data=data)
res = urllib.request.urlopen(req)
insp_id = json.loads(res.read())["inspection_id"]
print(f"Created Inspection ID: {insp_id}")

req2 = urllib.request.Request(f"http://127.0.0.1:8000/api/inspections/{insp_id}/analyze", data=b"")
res2 = urllib.request.urlopen(req2)
d2 = json.loads(res2.read())
print(f"Analyze Output: Rules Evaluated: {d2['rules_evaluated']}, Status: {d2['status']}")

req3 = urllib.request.Request(f"http://127.0.0.1:8000/api/inspections/{insp_id}")
res3 = urllib.request.urlopen(req3)
d3 = json.loads(res3.read())
print(f"Total Extracted Facts: {len(d3['facts'])}")
for cr in d3["compliance_results"]:
    print(f"  [{cr['rule_id']}] {cr['status']}: {cr['observed_value']}")

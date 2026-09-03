import urllib.request, json
req = urllib.request.Request("http://127.0.0.1:8000/api/inspections/INS-41754")
res = urllib.request.urlopen(req)
d = json.loads(res.read())
print("--- DEDUPLICATED FACTS (COUNT: " + str(len(d["facts"])) + ") ---")
for f in d["facts"]:
    val = str(f["value"]).encode("ascii", "replace").decode("ascii")
    print(f"  Field: {f['field_name']} | Value: {val}")
print("\n--- COMPLIANCE RESULTS (COUNT: " + str(len(d["compliance_results"])) + ") ---")
for cr in d["compliance_results"]:
    val = str(cr["observed_value"]).encode("ascii", "replace").decode("ascii")
    print(f"  {cr['rule_id']}: [{cr['status']}] {val}")

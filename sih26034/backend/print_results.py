import urllib.request, json
req = urllib.request.Request("http://127.0.0.1:8000/api/inspections/INS-40986")
res = urllib.request.urlopen(req)
d = json.loads(res.read())
for cr in d["compliance_results"]:
    val = str(cr["observed_value"]).encode("ascii", "replace").decode("ascii")
    print(f"{cr['rule_id']} | {cr['status']} | {val} | {cr['reason'][:50]}")

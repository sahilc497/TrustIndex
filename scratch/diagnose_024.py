import json
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.detector import verify

# Verify leave_024
with open(os.path.join(PROJECT_ROOT, "data", "eval_dataset.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

item_leave = [x for x in data if x["id"] == "leave_024"][0]
item_wfh = [x for x in data if x["id"] == "wfh_024"][0]

print("=== DIAGNOSTIC FOR LEAVE_024 ===")
print("Query:", item_leave["query"])
print("Source doc:", item_leave["source_doc"])
print("Source passage:", item_leave["source_passage"])
print("Correct answer:", item_leave["correct_answer"])
res_leave_corr = verify(item_leave["query"], item_leave["correct_answer"], [{"doc": item_leave["source_doc"], "text": item_leave["source_passage"]}])
print("leave_024 Correct Answer Verdict:")
print("  Trust Score:", res_leave_corr["trust_score"])
print("  Status:", res_leave_corr["status"])
print("  Explanation:", res_leave_corr["explanation"])
print("  Claims:")
for c in res_leave_corr["claims"]:
    print("    Claim:", c["claim"])
    print("    Consensus:", c["consensus"])
    for e in c["evidence"]:
        print(f"      Edge [{e['label']}]: {e['reason']}")

print("\nleave_024 Hallucinated Answer Verdict:")
res_leave_hallu = verify(item_leave["query"], item_leave["hallucinated_answer"], [{"doc": item_leave["source_doc"], "text": item_leave["source_passage"]}])
print("  Trust Score:", res_leave_hallu["trust_score"])
print("  Status:", res_leave_hallu["status"])
print("  Explanation:", res_leave_hallu["explanation"])

print("\n" + "="*50)
print("=== DIAGNOSTIC FOR WFH_024 ===")
print("Query:", item_wfh["query"])
print("Source doc:", item_wfh["source_doc"])
print("Source passage:", item_wfh["source_passage"])
print("Correct answer:", item_wfh["correct_answer"])
res_wfh_corr = verify(item_wfh["query"], item_wfh["correct_answer"], [{"doc": item_wfh["source_doc"], "text": item_wfh["source_passage"]}])
print("wfh_024 Correct Answer Verdict:")
print("  Trust Score:", res_wfh_corr["trust_score"])
print("  Status:", res_wfh_corr["status"])
print("  Explanation:", res_wfh_corr["explanation"])
print("  Claims:")
for c in res_wfh_corr["claims"]:
    print("    Claim:", c["claim"])
    print("    Consensus:", c["consensus"])
    for e in c["evidence"]:
        print(f"      Edge [{e['label']}]: {e['reason']}")

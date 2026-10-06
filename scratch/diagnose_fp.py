import json
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

with open(os.path.join(PROJECT_ROOT, "data", "eval_dataset.json"), "r", encoding="utf-8") as f:
    eval_data = json.load(f)

print("--- Entries with 024 in ID ---")
for item in eval_data:
    if "024" in item["id"] or "wfh" in item["id"] and "24" in item["id"]:
        print(f"[{item['id']}] error_type={item['error_type']}")
        print(f"  query: {item['query']}")
        print(f"  correct_answer: {item['correct_answer']}")
        print(f"  source_doc: {item['source_doc']}")
        print(f"  source_passage: {item['source_passage']}")

print("\n--- Check all rows in results/eval_results_upgraded.json for false positives ---")
with open(os.path.join(PROJECT_ROOT, "results", "eval_results_upgraded.json"), "r", encoding="utf-8") as f:
    eval_results = json.load(f)

for r in eval_results["rows"]:
    if r["correct_status"] == "Hallucinated":
        print(f"FALSE POSITIVE: [{r['id']}] ({r['error_type']})")
        print(f"  correct_answer: {r['correct_answer']}")
        print(f"  correct_trust_score: {r['correct_trust_score']}")
        print(f"  correct_status: {r['correct_status']}")

# Also check wfh_024 in eval_results
for r in eval_results["rows"]:
    if r["id"] in ["wfh_024", "wfh_24", "leave_024", "leave_24"]:
        print(f"[{r['id']}] correct_status={r['correct_status']}, correct_score={r['correct_trust_score']}, hallu_status={r['hallucinated_status']}, hallu_score={r['hallucinated_trust_score']}")

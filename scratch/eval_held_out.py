import json
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.detector import verify

with open(os.path.join(PROJECT_ROOT, "data", "held_out_eval_dataset.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data)} held-out pairs.")

strict_caught = 0
lenient_caught = 0

for item in data:
    ev = [{"doc": item["source_doc"], "text": item["source_passage"]}]
    res = verify(item["query"], item["hallucinated_answer"], ev)
    status = res["status"]
    score = res["trust_score"]
    if status == "Hallucinated":
        strict_caught += 1
        lenient_caught += 1
    elif status == "Uncertain":
        lenient_caught += 1
    print(f"[{item['id']}] status={status:<12} score={score:<5.1f} | {item['query']}")

print("-" * 60)
print(f"Strict catch rate:  {strict_caught}/{len(data)} ({strict_caught/len(data)*100:.1f}%)")
print(f"Lenient catch rate: {lenient_caught}/{len(data)} ({lenient_caught/len(data)*100:.1f}%)")

import json
import sys
sys.path.insert(0, '.')
from src.claim_extraction import extract_claims

with open('data/eval_dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

multi_claims = []
for item in data:
    for k in ['correct_answer', 'hallucinated_answer']:
        ans = item[k]
        claims = extract_claims(ans)
        if len(claims) > 1:
            multi_claims.append((item['id'], k, ans, claims))

print(f"Total multi-claim answers in eval_dataset: {len(multi_claims)}")
for qid, k, ans, claims in multi_claims[:10]:
    print(f"[{qid}] {k}: {ans}")
    for c in claims:
        print(f"    - {c}")

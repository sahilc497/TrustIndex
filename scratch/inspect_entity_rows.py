import json
import sys
sys.path.insert(0, '.')
from src.rag_baseline import retrieve_baseline

with open('results/rag_comparison.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_rows = data['all_rows']
entity_rows = [r for r in all_rows if r['category'] == 'Named Entity/Role']

print(f"Total entity rows: {len(entity_rows)}")

for idx, r in enumerate(entity_rows, 1):
    qid = r['id']
    query = r['query']
    ver_a = r['cond_a']
    ver_c = r['cond_c']
    ret = retrieve_baseline(query, top_k=2)
    print(f"\n[{idx}] ID: {qid} | Query: {query}")
    print(f"    Passage 1: {ret[0]['text'][:100]}...")
    print(f"    Passage 2: {ret[1]['text'][:100]}...")
    print(f"    Cond A: status={ver_a['status']}, score={ver_a['trust_score']}, claims={ver_a['num_claims']}")
    print(f"      Ans: {ver_a['answer']}")
    print(f"    Cond C: status={ver_c['status']}, score={ver_c['trust_score']}, claims={ver_c['num_claims']}")
    print(f"      Ans: {ver_c['answer']}")

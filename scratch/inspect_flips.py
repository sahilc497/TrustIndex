import json

with open('results/rag_comparison.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('--- A -> H, C -> Non-H (7 queries) ---')
for r in data['all_rows']:
    if r['cond_a']['status'] == 'Hallucinated' and r['cond_c']['status'] != 'Hallucinated':
        print(f"[{r['id']}] ({r['category']}): {r['query']}")
        print(f"    Cond A: {r['cond_a']['status']} (Score {r['cond_a']['trust_score']}) -> {r['cond_a']['answer'][:80]}")
        print(f"    Cond C: {r['cond_c']['status']} (Score {r['cond_c']['trust_score']}) -> {r['cond_c']['answer'][:80]}")

print('\n--- A -> Non-H, C -> H (6 queries) ---')
for r in data['all_rows']:
    if r['cond_a']['status'] != 'Hallucinated' and r['cond_c']['status'] == 'Hallucinated':
        print(f"[{r['id']}] ({r['category']}): {r['query']}")
        print(f"    Cond A: {r['cond_a']['status']} (Score {r['cond_a']['trust_score']}) -> {r['cond_a']['answer'][:80]}")
        print(f"    Cond C: {r['cond_c']['status']} (Score {r['cond_c']['trust_score']}) -> {r['cond_c']['answer'][:80]}")

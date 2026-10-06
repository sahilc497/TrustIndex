import sys
sys.path.insert(0, '.')
from src.rag_baseline import retrieve_baseline
from src.claim_extraction import extract_claims, split_sentences
from src.similarity import semantic_similarity
from src.contradiction import check_contradiction, extract_domain_entities

q = 'Which two roles must jointly provide written approval for full-time remote work?'
ret = retrieve_baseline(q, top_k=2)
for i, p in enumerate(ret):
    print(f"Passage {i+1} ({p['doc']}):\n{p['text']}\n")

ans_a = "Employees in customer-facing roles and full-time remote workers must jointly provide written approval for full-time remote work."
claims = extract_claims(ans_a)
print("Extracted claims from ans_a:")
for c in claims:
    print(" -", c)

print("\nEntities in claims:")
for c in claims:
    print(" Claim:", c)
    print(" Entities:", extract_domain_entities(c))

print("\nEntities in Passage 1:")
print(" Passage 1 entities:", extract_domain_entities(ret[0]['text']))

print("\nPassage 1 split sentences:")
sentences = split_sentences(ret[0]['text'])
for s in sentences:
    print(" Sentence:", s)
    print("   Entities:", extract_domain_entities(s))

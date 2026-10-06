import json
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.claim_extraction import split_sentences
from src.contradiction import extract_domain_entities

print("=== Scanning eval_dataset.json for multi-entity / multi-sentence passages ===")
with open(os.path.join(PROJECT_ROOT, "data", "eval_dataset.json"), "r", encoding="utf-8") as f:
    eval_data = json.load(f)

for item in eval_data:
    p = item["source_passage"]
    sents = split_sentences(p)
    ents = extract_domain_entities(p)
    all_ent_count = sum(len(v) for v in ents.values())
    if len(sents) > 1 or all_ent_count > 1:
        print(f"[{item['id']}] ({item['error_type']}) - Sentences: {len(sents)}, Entities ({all_ent_count}): {ents}")
        print(f"   Passage: {p}")

print("\n=== Scanning held_out_eval_dataset.json ===")
with open(os.path.join(PROJECT_ROOT, "data", "held_out_eval_dataset.json"), "r", encoding="utf-8") as f:
    held_data = json.load(f)

for item in held_data:
    p = item["source_passage"]
    sents = split_sentences(p)
    ents = extract_domain_entities(p)
    all_ent_count = sum(len(v) for v in ents.values())
    if len(sents) > 1 or all_ent_count > 1:
        print(f"[{item['id']}] ({item['error_type']}) - Sentences: {len(sents)}, Entities ({all_ent_count}): {ents}")
        print(f"   Passage: {p}")

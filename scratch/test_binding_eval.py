import json
import os
import re
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.claim_extraction import split_sentences
from src.similarity import semantic_similarity
from src.contradiction import extract_domain_entities, extract_numbers, _nli_fallback, ENTITY_CATEGORIES

# Check if ROLES_AND_AUTHORITIES has customer-facing roles
if "customer-facing roles" not in ENTITY_CATEGORIES["ROLES_AND_AUTHORITIES"]:
    ENTITY_CATEGORIES["ROLES_AND_AUTHORITIES"].append("customer-facing roles")
if "customer-facing" not in ENTITY_CATEGORIES["ROLES_AND_AUTHORITIES"]:
    ENTITY_CATEGORIES["ROLES_AND_AUTHORITIES"].append("customer-facing")

VERB_PATTERN = re.compile(
    r"\b(?:is|are|was|were|be|been|being|have|has|had|do|does|did|can|could|shall|should|will|would|may|might|must|require|requires|required|receive|receives|received|provide|provides|provided|apply|applies|applied|confirm|confirms|confirmed|submit|submits|submitted|pay|pays|paid|entitle|entitles|entitled)\b",
    re.IGNORECASE
)

COORDINATORS = re.compile(r"\s*,\s*(?:and|but)\s+|\s+(?:and|but)\s+", re.IGNORECASE)

def extract_claims_smart(answer: str):
    claims = []
    for sentence in split_sentences(answer):
        # Look for conjunctions
        matches = list(COORDINATORS.finditer(sentence))
        if not matches:
            claims.append(sentence.strip().rstrip("."))
            continue
        
        # Check if any conjunction separates two clauses that BOTH have verbs
        split_points = []
        last_end = 0
        current_part_start = 0
        
        for m in matches:
            left_part = sentence[current_part_start:m.start()].strip()
            right_part = sentence[m.end():].strip()
            # If comma present OR both parts have verbs, split
            has_comma = "," in sentence[m.start()-1:m.start()+1]
            left_has_verb = bool(VERB_PATTERN.search(left_part))
            right_has_verb = bool(VERB_PATTERN.search(right_part))
            
            if (has_comma and right_has_verb) or (left_has_verb and right_has_verb):
                split_points.append((m.start(), m.end()))
                current_part_start = m.end()
        
        if not split_points:
            claims.append(sentence.strip().rstrip("."))
        else:
            # Split along confirmed split points
            prev = 0
            for start, end in split_points:
                part = sentence[prev:start].strip().rstrip(".,")
                if len(part) > 3:
                    claims.append(part)
                prev = end
            tail = sentence[prev:].strip().rstrip(".,")
            if len(tail) > 3:
                claims.append(tail)
                
    return claims if claims else [answer.strip()]

def check_entity_mismatch_with_binding(claim: str, evidence: str, similarity_score: float):
    if similarity_score < 0.35:
        return None

    claim_entities = extract_domain_entities(claim)
    if not claim_entities:
        return None

    ev_sentences = split_sentences(evidence)
    passage_entities = extract_domain_entities(evidence)

    # 1. Restrict check to the evidence sentence most relevant to the claim's predicate
    if len(ev_sentences) > 1:
        scored_sents = [(s, semantic_similarity(claim, s)) for s in ev_sentences]
        scored_sents.sort(key=lambda x: x[1], reverse=True)
        best_sentence, best_sim = scored_sents[0]
    else:
        best_sentence = evidence
        best_sim = similarity_score

    best_sent_entities = extract_domain_entities(best_sentence)

    for cat, c_ents in claim_entities.items():
        if cat in best_sent_entities:
            best_ents = best_sent_entities[cat]
            unmatched = c_ents - best_ents
            if unmatched and not (c_ents & best_ents):
                # If the claimed entity exists elsewhere in the passage, it's a binding mismatch
                if cat in passage_entities and (c_ents & passage_entities[cat]):
                    return (
                        "CONTRADICTION",
                        f"Role/entity binding mismatch detected in category '{cat}': claim binds {sorted(c_ents)} "
                        f"to predicate/rule where evidence sentence specifies {sorted(best_ents)} "
                        f"(entity {sorted(c_ents & passage_entities[cat])} exists in passage but is bound to a different rule) [ENTITY_PRESENT_WRONG_BINDING]."
                    )
                else:
                    return (
                        "CONTRADICTION",
                        f"Entity/role substitution detected in category '{cat}': claim references {sorted(unmatched)} "
                        f"where evidence specifies {sorted(best_ents)}."
                    )
        elif cat in passage_entities:
            # Entity exists in passage, but best sentence has NO entity of this category,
            # or specifies a different rule altogether
            pass_ents = passage_entities[cat]
            if c_ents.issubset(pass_ents) and best_sim >= 0.40:
                # The claimed entity is in passage, but absent from the predicate-matching sentence
                return (
                    "CONTRADICTION",
                    f"Role/entity binding mismatch detected in category '{cat}': claim binds {sorted(c_ents)} "
                    f"to predicate/rule where evidence sentence does not support this entity "
                    f"(entity {sorted(c_ents)} exists in passage but is bound to a different rule) [ENTITY_PRESENT_WRONG_BINDING]."
                )
            elif not (c_ents & pass_ents):
                return (
                    "CONTRADICTION",
                    f"Entity/role substitution detected in category '{cat}': claim references {sorted(c_ents - pass_ents)} "
                    f"where evidence specifies {sorted(pass_ents)}."
                )

    return None

def check_contradiction_upgraded(claim: str, evidence: str, similarity_score: float):
    claim_numbers = extract_numbers(claim)
    evidence_numbers = extract_numbers(evidence)

    # Layer 1a: Numeric mismatch
    if claim_numbers and evidence_numbers:
        if not claim_numbers.issubset(evidence_numbers):
            unmatched = claim_numbers - evidence_numbers
            if unmatched and similarity_score >= 0.35:
                return (
                    "CONTRADICTION",
                    f"Claim contains number(s) {sorted(unmatched)} not present in evidence "
                    f"(evidence contains {sorted(evidence_numbers)}); likely numeric substitution."
                )

    # Layer 1b: Domain Entity / Role mismatch with sentence-level binding
    entity_check = check_entity_mismatch_with_binding(claim, evidence, similarity_score)
    if entity_check is not None:
        return entity_check

    # Layer 2: RoBERTa NLI
    return _nli_fallback(claim, evidence, similarity_score)

print("Functions compiled successfully.")

# Test wfh_019 end-to-end
from src.rag_baseline import retrieve_baseline
from src.trust_score import score_answer
from src.evidence_graph import build_claim_graph

def test_wfh_019_cond_a():
    q = "Which two roles must jointly provide written approval for full-time remote work?"
    ans_a = "Employees in customer-facing roles and full-time remote workers must jointly provide written approval for full-time remote work."
    ret = retrieve_baseline(q, top_k=2)
    
    claims = extract_claims_smart(ans_a)
    print("\nwfh_019 extracted claims:", claims)
    
    # Evaluate with upgraded contradiction logic
    claim_graphs = []
    for c in claims:
        edges = []
        for ev in ret:
            sim = semantic_similarity(c, ev["text"])
            label, reason = check_contradiction_upgraded(c, ev["text"], sim)
            edges.append({
                "doc": ev["doc"],
                "text": ev["text"],
                "similarity": round(sim, 3),
                "label": label,
                "reason": reason
            })
        
        # consensus
        support = sum(e["similarity"] for e in edges if e["label"] == "ENTAILMENT")
        contra = sum(e["similarity"] for e in edges if e["label"] == "CONTRADICTION")
        neutral = sum(e["similarity"] for e in edges if e["label"] == "NEUTRAL")
        consensus = (support - contra) / (support + contra + neutral + 1e-6)
        claim_graphs.append({"claim": c, "edges": edges, "consensus": consensus})
        
    res = score_answer(claim_graphs)
    print("wfh_019 Cond A result:")
    print("  Trust Score:", res["trust_score"])
    print("  Status:", res["status"])
    print("  Weakest Claim:", res["weakest_claim"]["claim"])
    for e in res["weakest_claim"]["edges"]:
        print(f"    Edge [{e['label']}]: {e['reason']}")
    return res

test_wfh_019_cond_a()

def run_eval_on_dataset(dataset_path):
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    rows = []
    for item in data:
        evidence = [{"doc": item["source_doc"], "text": item["source_passage"]}]
        
        # Verify correct answer
        claims_corr = extract_claims_smart(item["correct_answer"])
        claim_graphs_corr = []
        for c in claims_corr:
            edges = []
            for ev in evidence:
                sim = semantic_similarity(c, ev["text"])
                lbl, rsn = check_contradiction_upgraded(c, ev["text"], sim)
                edges.append({"doc": ev["doc"], "text": ev["text"], "similarity": round(sim, 3), "label": lbl, "reason": rsn})
            sup = sum(e["similarity"] for e in edges if e["label"] == "ENTAILMENT")
            con = sum(e["similarity"] for e in edges if e["label"] == "CONTRADICTION")
            neu = sum(e["similarity"] for e in edges if e["label"] == "NEUTRAL")
            claim_graphs_corr.append({"claim": c, "edges": edges, "consensus": (sup - con)/(sup + con + neu + 1e-6)})
        res_corr = score_answer(claim_graphs_corr)
        
        # Verify hallucinated answer
        claims_hallu = extract_claims_smart(item["hallucinated_answer"])
        claim_graphs_hallu = []
        for c in claims_hallu:
            edges = []
            for ev in evidence:
                sim = semantic_similarity(c, ev["text"])
                lbl, rsn = check_contradiction_upgraded(c, ev["text"], sim)
                edges.append({"doc": ev["doc"], "text": ev["text"], "similarity": round(sim, 3), "label": lbl, "reason": rsn})
            sup = sum(e["similarity"] for e in edges if e["label"] == "ENTAILMENT")
            con = sum(e["similarity"] for e in edges if e["label"] == "CONTRADICTION")
            neu = sum(e["similarity"] for e in edges if e["label"] == "NEUTRAL")
            claim_graphs_hallu.append({"claim": c, "edges": edges, "consensus": (sup - con)/(sup + con + neu + 1e-6)})
        res_hallu = score_answer(claim_graphs_hallu)
        
        rows.append({
            "id": item["id"],
            "error_type": item["error_type"],
            "correct_status": res_corr["status"],
            "correct_score": res_corr["trust_score"],
            "hallu_status": res_hallu["status"],
            "hallu_score": res_hallu["trust_score"],
            "hallu_explanation": res_hallu["weakest_claim"]["edges"][0]["reason"] if res_hallu["weakest_claim"] else ""
        })
        
    n = len(rows)
    tp = sum(1 for r in rows if r["hallu_status"] == "Hallucinated")
    fn = sum(1 for r in rows if r["hallu_status"] != "Hallucinated")
    fp = sum(1 for r in rows if r["correct_status"] == "Hallucinated")
    tn = sum(1 for r in rows if r["correct_status"] != "Hallucinated")
    
    prec = round(tp / (tp + fp), 3) if (tp + fp) else 0.0
    rec = round(tp / (tp + fn), 3) if (tp + fn) else 0.0
    f1 = round(2 * prec * rec / (prec + rec), 3) if (prec + rec) else 0.0
    acc = round((tp + tn) / (2 * n), 3)
    
    # By error type
    by_err = {}
    for r in rows:
        et = r["error_type"]
        if et not in by_err:
            by_err[et] = {"total": 0, "caught": 0, "lenient": 0}
        by_err[et]["total"] += 1
        if r["hallu_status"] == "Hallucinated":
            by_err[et]["caught"] += 1
            by_err[et]["lenient"] += 1
        elif r["hallu_status"] == "Uncertain":
            by_err[et]["lenient"] += 1
            
    for et, stats in by_err.items():
        stats["catch_rate"] = round(stats["caught"] / stats["total"], 3)
        stats["lenient_catch_rate"] = round(stats["lenient"] / stats["total"], 3)
        
    return {
        "n": n, "tp": tp, "fn": fn, "fp": fp, "tn": tn,
        "precision": prec, "recall": rec, "f1": f1, "accuracy": acc,
        "by_error_type": by_err,
        "rows": rows
    }

print("\nRunning evaluation on 77-pair eval_dataset.json...")
res_77 = run_eval_on_dataset("data/eval_dataset.json")
print("77-pair metrics:")
print(f"  Precision: {res_77['precision']} (baseline was 0.986)")
print(f"  Recall:    {res_77['recall']} (baseline was 0.922)")
print(f"  F1:        {res_77['f1']} (baseline was 0.953)")
print(f"  Accuracy:  {res_77['accuracy']} (baseline was 0.955)")
print(f"  Entity Swap: {res_77['by_error_type'].get('entity_swap', {})}")

print("\nRunning evaluation on 10-pair held_out_eval_dataset.json...")
res_held = run_eval_on_dataset("data/held_out_eval_dataset.json")
print("Held-out metrics:")
print(f"  Total: {res_held['n']}")
print(f"  Strict Caught: {res_held['tp']}/{res_held['n']} ({res_held['tp']/res_held['n']*100:.1f}%)")
lenient_caught = sum(1 for r in res_held['rows'] if r['hallu_status'] in ['Hallucinated', 'Uncertain'])
print(f"  Lenient Caught: {lenient_caught}/{res_held['n']} ({lenient_caught/res_held['n']*100:.1f}%)")

# Search for other multi-entity / multi-rule passages in eval_dataset and held-out
print("\nScanning for multi-entity passages across datasets...")
for name, dpath in [("eval_dataset.json", "data/eval_dataset.json"), ("held_out_eval_dataset.json", "data/held_out_eval_dataset.json")]:
    with open(dpath, "r", encoding="utf-8") as f:
        d = json.load(f)
    for item in d:
        p = item["source_passage"]
        sents = split_sentences(p)
        if len(sents) > 1:
            p_ents = extract_domain_entities(p)
            # count total entities across categories
            tot_ents = sum(len(v) for v in p_ents.values())
            if tot_ents > 1:
                print(f"[{name}] Multi-entity passage: {item['id']} ({item['error_type']})")
                print(f"  Passage has {len(sents)} sentences, entities: {p_ents}")
                print(f"  Query: {item['query']}")



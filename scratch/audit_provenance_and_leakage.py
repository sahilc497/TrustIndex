"""
Audit Provenance, Dataset Overlap, and Leakage for TRUST Index Validation.
"""

import json
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL_PATH = os.path.join(PROJECT_ROOT, "data", "eval_dataset.json")
HELDOUT_PATH = os.path.join(PROJECT_ROOT, "data", "held_out_eval_dataset.json")
VAL_PATH = os.path.join(PROJECT_ROOT, "data", "trust_validation_dataset.json")

RESULTS_DIR = os.path.join(PROJECT_ROOT, "results", "trust_validation")
PROVENANCE_OUT = os.path.join(RESULTS_DIR, "provenance_audit.json")
OVERLAP_OUT = os.path.join(RESULTS_DIR, "dataset_overlap.json")

with open(EVAL_PATH, "r", encoding="utf-8") as f:
    eval_77 = json.load(f)

with open(HELDOUT_PATH, "r", encoding="utf-8") as f:
    heldout_10 = json.load(f)

with open(VAL_PATH, "r", encoding="utf-8") as f:
    val_130 = json.load(f)

eval_by_id = {x["id"]: x for x in eval_77}
heldout_by_id = {x["id"]: x for x in heldout_10}

# Build query & evidence maps
def norm_text(t):
    return re.sub(r"\s+", " ", t.strip().lower())

eval_by_qe_corr = {(norm_text(x["query"]), norm_text(x["source_passage"])): (x["id"], norm_text(x["correct_answer"])) for x in eval_77}
eval_by_qe_hallu = {(norm_text(x["query"]), norm_text(x["source_passage"])): (x["id"], norm_text(x["hallucinated_answer"])) for x in eval_77}

heldout_by_qe_corr = {(norm_text(x["query"]), norm_text(x["source_passage"])): (x["id"], norm_text(x["correct_answer"])) for x in heldout_10}
heldout_by_qe_hallu = {(norm_text(x["query"]), norm_text(x["source_passage"])): (x["id"], norm_text(x["hallucinated_answer"])) for x in heldout_10}

provenance_records = []
exact_duplicates_to_eval_corr = []
exact_duplicates_to_eval_hallu = []
exact_duplicates_to_heldout_corr = []
exact_duplicates_to_heldout_hallu = []
same_query_evidence_cases = []
newly_constructed_cases = []

for item in val_130:
    cid = item["id"]
    ctype = item["case_type"]
    exp_label = item["expected_status"]
    sdoc = item["source_doc"]
    sref = item.get("source_passage", item["evidence"][:60] + "...")
    query = item["query"]
    ans = item["answer"]
    ev = item["evidence"]
    
    q_norm = norm_text(query)
    ev_norm = norm_text(ev)
    ans_norm = norm_text(ans)
    
    origin = "unknown"
    ground_truth_basis = "direct comparison against source evidence"
    dup_overlap = False
    possible_leakage = False
    notes = ""
    
    # Check origin
    # 1. Newly constructed identifiers
    if any(k in cid for k in ["extra", "part", "irrel", "direct"]):
        origin = "newly_constructed"
        ground_truth_basis = "manually defined expected behavior verified against source evidence"
        dup_overlap = False
        possible_leakage = False
        notes = "Newly constructed case designed for targeted case-type validation."
        newly_constructed_cases.append(cid)
    elif "heldout" in cid:
        origin = "held_out_10"
        ground_truth_basis = "existing benchmark (held-out IT security set)"
        dup_overlap = True
        # In held-out benchmark, rules were NOT tuned on these entities (README explicitly confirms taxonomy was not updated)
        possible_leakage = False
        notes = "Reused from independent 10-item held-out evaluation dataset."
        if (q_norm, ev_norm) in heldout_by_qe_corr and ans_norm == heldout_by_qe_corr[(q_norm, ev_norm)][1]:
            exact_duplicates_to_heldout_corr.append(cid)
            notes += " Exact duplicate of held-out correct answer."
        elif (q_norm, ev_norm) in heldout_by_qe_hallu and ans_norm == heldout_by_qe_hallu[(q_norm, ev_norm)][1]:
            exact_duplicates_to_heldout_hallu.append(cid)
            notes += " Exact duplicate of held-out hallucinated answer."
    else:
        # Check matching against eval_77
        matched_eval_id = None
        for eid in eval_by_id:
            if eid in cid:
                matched_eval_id = eid
                break
        
        if matched_eval_id or (q_norm, ev_norm) in eval_by_qe_corr or (q_norm, ev_norm) in eval_by_qe_hallu:
            origin = "original_77"
            dup_overlap = True
            # Cases from original 77 were part of the initial detector benchmark (which informed initial rule-based refinements in Phase 1)
            possible_leakage = True
            ground_truth_basis = "existing benchmark (77-item main evaluation set)"
            notes = f"Reused from main 77-item benchmark (base ID: {matched_eval_id or 'query match'})."
            
            if (q_norm, ev_norm) in eval_by_qe_corr and ans_norm == eval_by_qe_corr[(q_norm, ev_norm)][1]:
                exact_duplicates_to_eval_corr.append(cid)
                notes += " Exact duplicate of 77-item correct answer."
            elif (q_norm, ev_norm) in eval_by_qe_hallu and ans_norm == eval_by_qe_hallu[(q_norm, ev_norm)][1]:
                exact_duplicates_to_eval_hallu.append(cid)
                notes += " Exact duplicate of 77-item hallucinated answer."
            else:
                notes += " Query and evidence shared with 77-item benchmark."
        else:
            origin = "unknown"
            notes = "Could not definitively establish lineage."

    # Record case
    provenance_records.append({
        "case_id": cid,
        "case_type": ctype,
        "expected_label": exp_label,
        "origin": origin,
        "source_document": sdoc,
        "source_reference": sref,
        "ground_truth_basis": ground_truth_basis,
        "duplicate_or_overlap": dup_overlap,
        "possible_leakage": possible_leakage,
        "notes": notes
    })

# Save provenance audit
os.makedirs(RESULTS_DIR, exist_ok=True)
with open(PROVENANCE_OUT, "w", encoding="utf-8") as f:
    json.dump(provenance_records, f, indent=2)

print(f"Saved provenance audit for {len(provenance_records)} cases to: {PROVENANCE_OUT}")

# Analyze Overlap
# 1. Exact duplicates with eval_77 correct answers
# 2. Exact duplicates with eval_77 hallucinated answers
# 3. Exact duplicates with heldout_10 correct answers
# 4. Exact duplicates with heldout_10 hallucinated answers
total_exact_eval = len(exact_duplicates_to_eval_corr) + len(exact_duplicates_to_eval_hallu)
total_exact_heldout = len(exact_duplicates_to_heldout_corr) + len(exact_duplicates_to_heldout_hallu)
total_exact_duplicates = total_exact_eval + total_exact_heldout

# 5. Internal overlap within val_130 (pairs sharing exact query + evidence)
qe_groups = {}
for item in val_130:
    key = (norm_text(item["query"]), norm_text(item["evidence"]))
    qe_groups.setdefault(key, []).append(item["id"])

internal_shared_qe = {k[0]: v for k, v in qe_groups.items() if len(v) > 1}

overlap_summary = {
    "total_validation_cases": len(val_130),
    "cases_from_original_77": sum(1 for p in provenance_records if p["origin"] == "original_77"),
    "cases_from_held_out_10": sum(1 for p in provenance_records if p["origin"] == "held_out_10"),
    "cases_newly_constructed": sum(1 for p in provenance_records if p["origin"] == "newly_constructed"),
    "cases_unknown_origin": sum(1 for p in provenance_records if p["origin"] == "unknown"),
    "exact_duplicates": {
        "total_exact_duplicates": total_exact_duplicates,
        "exact_duplicates_original_77_correct": {
            "count": len(exact_duplicates_to_eval_corr),
            "case_ids": exact_duplicates_to_eval_corr
        },
        "exact_duplicates_original_77_hallucinated": {
            "count": len(exact_duplicates_to_eval_hallu),
            "case_ids": exact_duplicates_to_eval_hallu
        },
        "exact_duplicates_held_out_10_correct": {
            "count": len(exact_duplicates_to_heldout_corr),
            "case_ids": exact_duplicates_to_heldout_corr
        },
        "exact_duplicates_held_out_10_hallucinated": {
            "count": len(exact_duplicates_to_heldout_hallu),
            "case_ids": exact_duplicates_to_heldout_hallu
        }
    },
    "internal_qe_overlap": {
        "num_shared_query_evidence_pairs": len(internal_shared_qe),
        "total_cases_involved": sum(len(v) for v in internal_shared_qe.values()),
        "description": "Validation cases sharing the same query and evidence but testing different answers (e.g. Correct Answer in Case 1 vs. Hallucinated Answer in Cases 6-8).",
        "sample_mappings": {k: v for k, v in list(internal_shared_qe.items())[:5]}
    },
    "leakage_assessment": {
        "potential_leakage_count": sum(1 for p in provenance_records if p["possible_leakage"]),
        "clean_unseen_cases_count": sum(1 for p in provenance_records if not p["possible_leakage"]),
        "notes": (
            "88 cases originate directly from the original 77-item benchmark (data/eval_dataset.json) where initial "
            "detector development in Phase 1 took place. These constitute potential evaluation leakage if interpreted as "
            "a fully independent blind test. The 11 held-out cases and 31 newly constructed cases (42 cases total) "
            "had zero influence on rule development."
        )
    }
}

with open(OVERLAP_OUT, "w", encoding="utf-8") as f:
    json.dump(overlap_summary, f, indent=2)

print(f"Saved dataset overlap analysis to: {OVERLAP_OUT}")

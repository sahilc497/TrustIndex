import json
import os
import sys
from scipy.stats import binomtest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.rag_baseline import retrieve_baseline

with open(os.path.join(PROJECT_ROOT, "results", "rag_comparison.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

all_rows = data["all_rows"]
print(f"Loaded {len(all_rows)} rows.")

# 1. McNemar test for pairwise comparisons:
# Comparisons: A vs B, A vs C, A vs D, B vs D, C vs D
# For paired binary outcome: Hallucinated (H) vs Not-Hallucinated (NH)
# Status == 'Hallucinated' -> H
# Status in ['Trusted', 'Uncertain'] -> NH

pairs = [
    ("cond_a", "cond_b", "A vs B (Base Prompt: Baseline vs SBERT Re-rank)"),
    ("cond_a", "cond_c", "A vs C (Baseline Ret: Baseline vs Citation Prompt)"),
    ("cond_a", "cond_d", "A vs D (Baseline vs Full Improved)"),
    ("cond_b", "cond_d", "B vs D (SBERT Ret: Baseline vs Citation Prompt)"),
    ("cond_c", "cond_d", "C vs D (Citation Prompt: Baseline vs SBERT Re-rank)")
]

print("\n" + "="*80)
print("1. MCNEMAR TESTS ON PAIRED (HALLUCINATED vs NOT-HALLUCINATED) OUTCOMES (N=77)")
print("="*80)

mcnemar_results = {}

for k1, k2, label in pairs:
    # Contingency table:
    # a: k1=H, k2=H
    # b: k1=H, k2=NH (discordant: H -> NH)
    # c: k1=NH, k2=H (discordant: NH -> H)
    # d: k1=NH, k2=NH
    a = sum(1 for r in all_rows if r[k1]["status"] == "Hallucinated" and r[k2]["status"] == "Hallucinated")
    b = sum(1 for r in all_rows if r[k1]["status"] == "Hallucinated" and r[k2]["status"] != "Hallucinated")
    c = sum(1 for r in all_rows if r[k1]["status"] != "Hallucinated" and r[k2]["status"] == "Hallucinated")
    d = sum(1 for r in all_rows if r[k1]["status"] != "Hallucinated" and r[k2]["status"] != "Hallucinated")
    
    total = a + b + c + d
    n_discordant = b + c
    
    # Exact binomial test (two-sided)
    if n_discordant > 0:
        res_binom = binomtest(b, n_discordant, 0.5, alternative='two-sided')
        p_exact = res_binom.pvalue
        # Edwards continuity correction chi-square
        chi2 = float((abs(b - c) - 1)**2 / n_discordant) if abs(b - c) >= 1 else 0.0
    else:
        p_exact = 1.0
        chi2 = 0.0
        
    k1_h = sum(1 for r in all_rows if r[k1]["status"] == "Hallucinated")
    k2_h = sum(1 for r in all_rows if r[k2]["status"] == "Hallucinated")
    
    mcnemar_results[label] = {
        "k1": k1, "k2": k2,
        "k1_hallu": k1_h, "k1_hallu_pct": round(k1_h/total*100, 1),
        "k2_hallu": k2_h, "k2_hallu_pct": round(k2_h/total*100, 1),
        "a_both_H": a,
        "b_k1H_k2NH": b,
        "c_k1NH_k2H": c,
        "d_both_NH": d,
        "n_discordant": n_discordant,
        "chi2_continuity": float(round(chi2, 4)),
        "p_exact": float(p_exact),
        "p_exact_fmt": f"{p_exact:.4f}" if p_exact >= 0.0001 else f"{p_exact:.2e}",
        "significant_p05": bool(p_exact < 0.05)
    }
    
    print(f"\n--- {label} ---")
    print(f"  Marginals: {k1.upper()} Hallucinated = {k1_h}/77 ({k1_h/total*100:.1f}%), {k2.upper()} Hallucinated = {k2_h}/77 ({k2_h/total*100:.1f}%)")
    print(f"  Contingency Table:")
    print(f"                   {k2.upper()} Hallu    {k2.upper()} Not-Hallu    Total")
    print(f"    {k1.upper()} Hallu        {a:<14} {b:<18} {a+b}")
    print(f"    {k1.upper()} Not-Hallu    {c:<14} {d:<18} {c+d}")
    print(f"    Total             {a+c:<14} {b+d:<18} {total}")
    print(f"  Discordant pairs (b, c) = ({b}, {c}), total discordant = {n_discordant}")
    print(f"  McNemar Chi2 (continuity corrected): {chi2:.4f}")
    print(f"  Exact Binomial p-value: {p_exact:.4f}")
    print(f"  Statistically significant at p < 0.05: {bool(p_exact < 0.05)}")

# 2. Specifically check A vs C flips
print("\n" + "="*80)
print("2. A vs C SPECIFIC FLIP REPORT")
print("="*80)
a_c_b = mcnemar_results["A vs C (Baseline Ret: Baseline vs Citation Prompt)"]["b_k1H_k2NH"]
a_c_c = mcnemar_results["A vs C (Baseline Ret: Baseline vs Citation Prompt)"]["c_k1NH_k2H"]
a_c_p = mcnemar_results["A vs C (Baseline Ret: Baseline vs Citation Prompt)"]["p_exact"]

print(f"Queries flipping Hallucinated (Cond A) -> Not-Hallucinated (Cond C): {a_c_b}")
print(f"Queries flipping Not-Hallucinated (Cond A) -> Hallucinated (Cond C): {a_c_c}")
print(f"Net change: 18 (23.4%) -> 17 (22.1%)")
print(f"Exact McNemar p-value: {a_c_p:.4f}")
print(f"Is difference statistically significant at p < 0.05? {'YES' if a_c_p < 0.05 else 'NO (p = ' + str(round(a_c_p, 4)) + ')'}")

# Print the specific queries that flipped for A vs C
print("\nQueries that flipped Hallucinated in A -> Not-Hallucinated in C:")
for r in all_rows:
    if r["cond_a"]["status"] == "Hallucinated" and r["cond_c"]["status"] != "Hallucinated":
        print(f"  - [{r['id']}] ({r['category']}): {r['query']}")
        print(f"      Cond A: {r['cond_a']['status']} (Score {r['cond_a']['trust_score']}) | Cond C: {r['cond_c']['status']} (Score {r['cond_c']['trust_score']})")

print("\nQueries that flipped Not-Hallucinated in A -> Hallucinated in C:")
for r in all_rows:
    if r["cond_a"]["status"] != "Hallucinated" and r["cond_c"]["status"] == "Hallucinated":
        print(f"  - [{r['id']}] ({r['category']}): {r['query']}")
        print(f"      Cond A: {r['cond_a']['status']} (Score {r['cond_a']['trust_score']}) | Cond C: {r['cond_c']['status']} (Score {r['cond_c']['trust_score']})")

# 3. Category level breakdown with raw counts
print("\n" + "="*80)
print("3. CATEGORY LEVEL BREAKDOWNS WITH RAW COUNTS")
print("="*80)
categories = ["Number/Quantity", "Neither/Semantic", "Named Entity/Role"]

for cat in categories:
    cat_rows = [r for r in all_rows if r["category"] == cat]
    n_cat = len(cat_rows)
    print(f"\nCategory: {cat} (n = {n_cat})")
    for cond_key, cond_name in [("cond_a", "Cond A"), ("cond_b", "Cond B"), ("cond_c", "Cond C"), ("cond_d", "Cond D")]:
        h_cnt = sum(1 for r in cat_rows if r[cond_key]["status"] == "Hallucinated")
        t_cnt = sum(1 for r in cat_rows if r[cond_key]["status"] == "Trusted")
        u_cnt = sum(1 for r in cat_rows if r[cond_key]["status"] == "Uncertain")
        mean_s = sum(r[cond_key]["trust_score"] for r in cat_rows) / n_cat
        h_pct = (h_cnt / n_cat) * 100
        print(f"  {cond_name}: Hallucinated = {h_pct:.1f}% ({h_cnt}/{n_cat}) | Trusted = {t_cnt}/{n_cat} | Uncertain = {u_cnt}/{n_cat} | Mean = {mean_s:.1f}")

# 4. Pull 4 full transcripts from Named Entity/Role where both A and C scored Non-Hallucinated
print("\n" + "="*80)
print("4. FULL EXAMPLE TRANSCRIPTS: NAMED ENTITY / ROLE (Both Cond A & C Non-Hallucinated)")
print("="*80)

entity_rows = [r for r in all_rows if r["category"] == "Named Entity/Role" and r["cond_a"]["status"] != "Hallucinated" and r["cond_c"]["status"] != "Hallucinated"]
print(f"Total Named Entity/Role rows where both A and C are Non-Hallucinated: {len(entity_rows)}")

# Let's take the first 4 examples
sample_entity_rows = entity_rows[:4]
samples_output = []

for idx, r in enumerate(sample_entity_rows, 1):
    qid = r["id"]
    query = r["query"]
    ret_passages = retrieve_baseline(query, top_k=2)
    
    sample_info = {
        "sample_num": idx,
        "id": qid,
        "query": query,
        "retrieved_passages": [p["text"] for p in ret_passages],
        "cond_a": {
            "answer": r["cond_a"]["answer"],
            "trust_score": r["cond_a"]["trust_score"],
            "status": r["cond_a"]["status"],
            "num_claims": r["cond_a"]["num_claims"],
            "explanation": r["cond_a"]["explanation"]
        },
        "cond_c": {
            "answer": r["cond_c"]["answer"],
            "trust_score": r["cond_c"]["trust_score"],
            "status": r["cond_c"]["status"],
            "num_claims": r["cond_c"]["num_claims"],
            "explanation": r["cond_c"]["explanation"]
        }
    }
    samples_output.append(sample_info)
    
    print(f"\n--- Example {idx}: [{qid}] ---")
    print(f"Query: {query}")
    print("Retrieved Passages:")
    for pi, p in enumerate(ret_passages, 1):
        print(f"  [{pi}] {p['text']}")
    print(f"Condition A (Base Prompt):")
    print(f"  Answer: {r['cond_a']['answer']}")
    print(f"  Verdict: {r['cond_a']['status']} (Trust Score: {r['cond_a']['trust_score']}, Claims: {r['cond_a']['num_claims']})")
    print(f"  Explanation: {r['cond_a']['explanation']}")
    print(f"Condition C (Citation Prompt):")
    print(f"  Answer: {r['cond_c']['answer']}")
    print(f"  Verdict: {r['cond_c']['status']} (Trust Score: {r['cond_c']['trust_score']}, Claims: {r['cond_c']['num_claims']})")
    print(f"  Explanation: {r['cond_c']['explanation']}")

with open(os.path.join(PROJECT_ROOT, "scratch", "mcnemar_output.json"), "w", encoding="utf-8") as f:
    json.dump({
        "mcnemar": mcnemar_results,
        "samples": samples_output
    }, f, indent=2)
print("\nWrote scratch/mcnemar_output.json")

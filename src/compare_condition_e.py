"""
Condition E Evaluation and Comparison Harness.

Evaluates Condition E (Hybrid RRF Retrieval + Concise Grounded Prompt) across:
1. The 77 queries from data/eval_dataset.json
2. The 10 held-out queries from data/held_out_eval_dataset.json (combined n=87)

Judged objectively by the frozen TRUST Index detector.
Computes McNemar's paired test against Condition A (primary) and Conditions B, C, D.
Saves raw per-query predictions and summary statistics to results/condition_e_comparison.json.
"""

import json
import os
import statistics
import sys
import time
from scipy.stats import binomtest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.rag_condition_e import make_condition_e_prompt
from src.rag_hybrid_retrieval import retrieve_hybrid_rrf
from src.rag_baseline import retrieve_baseline
from src.llm_client import generate, check_is_truncated
from src.detector import verify


def make_cond_a_prompt(query: str, context: str) -> str:
    return (
        f"<|user|>\n"
        f"Answer the question using this context: {context}\n\n"
        f"Question: {query}<|assistant|>\n"
    )


def compute_stats(records, key="cond_e"):
    n = len(records)
    if n == 0:
        return {}
    scores = [r[key]["trust_score"] for r in records]
    claims = [r[key]["num_claims"] for r in records]
    trusted = sum(1 for r in records if r[key]["status"] == "Trusted")
    uncertain = sum(1 for r in records if r[key]["status"] == "Uncertain")
    hallu = sum(1 for r in records if r[key]["status"] == "Hallucinated")
    trunc = sum(1 for r in records if r[key]["is_truncated"])

    return {
        "n": n,
        "mean_trust_score": round(statistics.mean(scores), 2),
        "median_trust_score": round(statistics.median(scores), 2),
        "pct_trusted": round(trusted / n * 100, 1),
        "count_trusted": trusted,
        "pct_uncertain": round(uncertain / n * 100, 1),
        "count_uncertain": uncertain,
        "pct_hallucinated": round(hallu / n * 100, 1),
        "count_hallucinated": hallu,
        "mean_atomic_claims": round(statistics.mean(claims), 2),
        "truncation_rate": round(trunc / n * 100, 1),
        "count_truncated": trunc
    }


def mcnemar_test(records, k1, k2):
    # a: both H, b: k1=H and k2!=H, c: k1!=H and k2=H, d: both != H
    a = sum(1 for r in records if r[k1]["status"] == "Hallucinated" and r[k2]["status"] == "Hallucinated")
    b = sum(1 for r in records if r[k1]["status"] == "Hallucinated" and r[k2]["status"] != "Hallucinated")
    c = sum(1 for r in records if r[k1]["status"] != "Hallucinated" and r[k2]["status"] == "Hallucinated")
    d = sum(1 for r in records if r[k1]["status"] != "Hallucinated" and r[k2]["status"] != "Hallucinated")

    n_discordant = b + c
    if n_discordant > 0:
        p_val = float(binomtest(b, n_discordant, 0.5, alternative="two-sided").pvalue)
        chi2 = float((abs(b - c) - 1)**2 / n_discordant) if abs(b - c) >= 1 else 0.0
    else:
        p_val = 1.0
        chi2 = 0.0

    k1_h = sum(1 for r in records if r[k1]["status"] == "Hallucinated")
    k2_h = sum(1 for r in records if r[k2]["status"] == "Hallucinated")
    total = len(records)

    return {
        "k1": k1, "k2": k2,
        "total": total,
        "k1_hallu": k1_h, "k1_hallu_pct": round(k1_h / total * 100, 1),
        "k2_hallu": k2_h, "k2_hallu_pct": round(k2_h / total * 100, 1),
        "a_both_H": a,
        "b_k1H_k2NH": b,
        "c_k1NH_k2H": c,
        "d_both_NH": d,
        "n_discordant": n_discordant,
        "chi2_continuity": round(chi2, 4),
        "p_exact": p_val,
        "p_exact_fmt": f"{p_val:.4f}" if p_val >= 0.0001 else f"{p_val:.2e}",
        "significant_p05": bool(p_val < 0.05)
    }


def main():
    print("=" * 80)
    print("RUNNING CONDITION E EVALUATION (Hybrid RRF + Concise Grounded Prompt)")
    print("=" * 80)

    # 1. Load existing 2x2 comparison data for conditions A-D
    comp_file = os.path.join(PROJECT_ROOT, "results", "rag_comparison.json")
    with open(comp_file, "r", encoding="utf-8") as f:
        comp_data = json.load(f)

    existing_rows_77 = {r["id"]: r for r in comp_data["all_rows"]}

    # 2. Load eval_dataset.json (77 items)
    with open(os.path.join(PROJECT_ROOT, "data", "eval_dataset.json"), "r", encoding="utf-8") as f:
        main_77 = json.load(f)

    # 3. Load held_out_eval_dataset.json (10 items)
    with open(os.path.join(PROJECT_ROOT, "data", "held_out_eval_dataset.json"), "r", encoding="utf-8") as f:
        held_10 = json.load(f)

    combined_87 = main_77 + held_10
    print(f"Loaded {len(main_77)} main queries + {len(held_10)} held-out queries = {len(combined_87)} total.")

    evaluated_records = []
    t0 = time.time()

    for idx, item in enumerate(combined_87, 1):
        qid = item["id"]
        query = item["query"]
        is_heldout = (idx > len(main_77))

        # Retrieve via Hybrid RRF
        ret_e = retrieve_hybrid_rrf(query, top_k=2)
        ctx_e = " ".join([p["text"] for p in ret_e])

        # Generate Condition E response
        p_e = make_condition_e_prompt(query, ctx_e)
        ans_e, trunc_e, tok_e = generate(p_e, max_new_tokens=110, return_meta=True)

        # Verify using frozen detector
        ver_e = verify(query, ans_e, ret_e)

        cond_e_data = {
            "name": "Hybrid RRF + Concise Grounded Prompt",
            "answer": ans_e,
            "trust_score": round(ver_e["trust_score"], 2),
            "status": ver_e["status"],
            "num_claims": len(ver_e["claims"]),
            "is_truncated": trunc_e,
            "tokens": tok_e,
            "explanation": ver_e["explanation"]
        }

        # For the 77 main queries, fetch existing cond_a, cond_b, cond_c, cond_d
        if qid in existing_rows_77:
            ex = existing_rows_77[qid]
            cond_a_data = ex["cond_a"]
            cond_b_data = ex["cond_b"]
            cond_c_data = ex["cond_c"]
            cond_d_data = ex["cond_d"]
        else:
            # Held-out query: generate Condition A response as well for paired comparison
            ret_a = retrieve_baseline(query, top_k=2)
            ctx_a = " ".join([p["text"] for p in ret_a])
            p_a = make_cond_a_prompt(query, ctx_a)
            ans_a, trunc_a, tok_a = generate(p_a, max_new_tokens=110, return_meta=True)
            ver_a = verify(query, ans_a, ret_a)
            cond_a_data = {
                "name": "Base Ret + Base Prompt",
                "answer": ans_a,
                "trust_score": round(ver_a["trust_score"], 2),
                "status": ver_a["status"],
                "num_claims": len(ver_a["claims"]),
                "is_truncated": trunc_a,
                "tokens": tok_a,
                "explanation": ver_a["explanation"]
            }
            cond_b_data = None
            cond_c_data = None
            cond_d_data = None

        record = {
            "id": qid,
            "query": query,
            "is_heldout": is_heldout,
            "cond_e": cond_e_data,
            "cond_a": cond_a_data,
            "cond_b": cond_b_data,
            "cond_c": cond_c_data,
            "cond_d": cond_d_data
        }
        evaluated_records.append(record)

        if idx % 10 == 0 or idx == len(combined_87):
            print(f"[{idx}/{len(combined_87)}] Processed {qid} -> Status: {cond_e_data['status']} (Score: {cond_e_data['trust_score']})", flush=True)

    elapsed = round(time.time() - t0, 1)
    print(f"\nCompleted generation and verification in {elapsed}s.")

    # 4. Compute statistics
    records_77 = evaluated_records[:77]
    records_87 = evaluated_records

    stats_77_e = compute_stats(records_77, "cond_e")
    stats_77_a = compute_stats(records_77, "cond_a")
    stats_77_b = compute_stats(records_77, "cond_b")
    stats_77_c = compute_stats(records_77, "cond_c")
    stats_77_d = compute_stats(records_77, "cond_d")

    stats_87_e = compute_stats(records_87, "cond_e")
    stats_87_a = compute_stats(records_87, "cond_a")

    # 5. McNemar paired tests
    mcnemar_77_e_vs_a = mcnemar_test(records_77, "cond_e", "cond_a")
    mcnemar_77_e_vs_b = mcnemar_test(records_77, "cond_e", "cond_b")
    mcnemar_77_e_vs_c = mcnemar_test(records_77, "cond_e", "cond_c")
    mcnemar_77_e_vs_d = mcnemar_test(records_77, "cond_e", "cond_d")

    mcnemar_87_e_vs_a = mcnemar_test(records_87, "cond_e", "cond_a")

    # Print summary tables
    print("\n" + "=" * 80)
    print("CONDITION E RESULTS (MAIN SET N=77)")
    print("=" * 80)
    print(f"{'Condition':<32} {'Mean':<8} {'Median':<8} {'% Trusted':<14} {'% Uncertain':<14} {'% Hallu':<14} {'Claims/Ans':<12}")
    print("-" * 102)
    for name, s in [
        ("A: Baseline (Lexical+Std)", stats_77_a),
        ("B: Re-Ranking (SBERT+Std)", stats_77_b),
        ("C: Citation (Lexical+Cite)", stats_77_c),
        ("D: Combined (SBERT+Cite)", stats_77_d),
        ("E: Hybrid RRF + Concise Ground", stats_77_e)
    ]:
        print(f"{name:<32} {s['mean_trust_score']:<8} {s['median_trust_score']:<8} "
              f"{s['pct_trusted']}% ({s['count_trusted']})    "
              f"{s['pct_uncertain']}% ({s['count_uncertain']})    "
              f"{s['pct_hallucinated']}% ({s['count_hallucinated']})    "
              f"{s['mean_atomic_claims']:<12}")

    print("\n" + "=" * 80)
    print("COMBINED DATASET RESULTS (N=87: 77 Main + 10 Held-out)")
    print("=" * 80)
    print(f"{'Condition':<32} {'Mean':<8} {'Median':<8} {'% Trusted':<14} {'% Uncertain':<14} {'% Hallu':<14} {'Claims/Ans':<12}")
    print("-" * 102)
    for name, s in [
        ("A: Baseline (Lexical+Std)", stats_87_a),
        ("E: Hybrid RRF + Concise Ground", stats_87_e)
    ]:
        print(f"{name:<32} {s['mean_trust_score']:<8} {s['median_trust_score']:<8} "
              f"{s['pct_trusted']}% ({s['count_trusted']})    "
              f"{s['pct_uncertain']}% ({s['count_uncertain']})    "
              f"{s['pct_hallucinated']}% ({s['count_hallucinated']})    "
              f"{s['mean_atomic_claims']:<12}")

    print("\n" + "=" * 80)
    print("MCNEMAR SIGNIFICANCE TESTS")
    print("=" * 80)
    print(f"E vs A (Main 77):  Discordant (E_H, A_NH)={mcnemar_77_e_vs_a['b_k1H_k2NH']}, (E_NH, A_H)={mcnemar_77_e_vs_a['c_k1NH_k2H']} | p={mcnemar_77_e_vs_a['p_exact_fmt']} | Significant: {mcnemar_77_e_vs_a['significant_p05']}")
    print(f"E vs B (Main 77):  Discordant (E_H, B_NH)={mcnemar_77_e_vs_b['b_k1H_k2NH']}, (E_NH, B_H)={mcnemar_77_e_vs_b['c_k1NH_k2H']} | p={mcnemar_77_e_vs_b['p_exact_fmt']} | Significant: {mcnemar_77_e_vs_b['significant_p05']}")
    print(f"E vs C (Main 77):  Discordant (E_H, C_NH)={mcnemar_77_e_vs_c['b_k1H_k2NH']}, (E_NH, C_H)={mcnemar_77_e_vs_c['c_k1NH_k2H']} | p={mcnemar_77_e_vs_c['p_exact_fmt']} | Significant: {mcnemar_77_e_vs_c['significant_p05']}")
    print(f"E vs D (Main 77):  Discordant (E_H, D_NH)={mcnemar_77_e_vs_d['b_k1H_k2NH']}, (E_NH, D_H)={mcnemar_77_e_vs_d['c_k1NH_k2H']} | p={mcnemar_77_e_vs_d['p_exact_fmt']} | Significant: {mcnemar_77_e_vs_d['significant_p05']}")
    print(f"E vs A (Comb 87):  Discordant (E_H, A_NH)={mcnemar_87_e_vs_a['b_k1H_k2NH']}, (E_NH, A_H)={mcnemar_87_e_vs_a['c_k1NH_k2H']} | p={mcnemar_87_e_vs_a['p_exact_fmt']} | Significant: {mcnemar_87_e_vs_a['significant_p05']}")

    # Save to results/condition_e_comparison.json
    output_data = {
        "metadata": {
            "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "max_new_tokens": 110,
            "generator_confound_status": "Identical generator used across all conditions A-E (zero model discrepancy)",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "stats_77": {
            "condition_a": stats_77_a,
            "condition_b": stats_77_b,
            "condition_c": stats_77_c,
            "condition_d": stats_77_d,
            "condition_e": stats_77_e
        },
        "stats_87_combined": {
            "condition_a": stats_87_a,
            "condition_e": stats_87_e
        },
        "mcnemar_tests": {
            "77_e_vs_a": mcnemar_77_e_vs_a,
            "77_e_vs_b": mcnemar_77_e_vs_b,
            "77_e_vs_c": mcnemar_77_e_vs_c,
            "77_e_vs_d": mcnemar_77_e_vs_d,
            "87_e_vs_a": mcnemar_87_e_vs_a
        },
        "all_rows": evaluated_records
    }

    out_path = os.path.join(PROJECT_ROOT, "results", "condition_e_comparison.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nSaved full raw results to {out_path}")


if __name__ == "__main__":
    main()

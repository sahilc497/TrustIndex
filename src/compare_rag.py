"""
Phase 4: 2x2 Controlled Ablation Study of RAG Improvement Mechanisms.

Isolates two independent variables:
1. Retrieval: Baseline (Naive Lexical Top-2) vs. Improved (SBERT Re-ranking Top-10 -> Top-2)
2. Prompt: Baseline (Standard Prompt) vs. Improved (Citation-Forced Prompt)

Evaluates all FOUR conditions across the 77 queries from data/eval_dataset.json:
- Condition A: Baseline Retrieval + Baseline Prompt
- Condition B: Improved Retrieval + Baseline Prompt  (Isolates Re-Ranking)
- Condition C: Baseline Retrieval + Citation Prompt  (Isolates Citation Prompting)
- Condition D: Improved Retrieval + Citation Prompt  (Combined)

Judged objectively by the frozen TRUST Index detector.
"""

import json
import os
import statistics
import sys
import time
from typing import Dict, List, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.rag_baseline import retrieve_baseline
from src.rag_improved import retrieve_improved
from src.llm_client import generate
from src.detector import verify


def categorize_query(error_type: str) -> str:
    if error_type in ["numeric_substitution", "date_change"]:
        return "Number/Quantity"
    elif error_type in ["entity_swap"]:
        return "Named Entity/Role"
    else:
        return "Neither/Semantic"


def make_baseline_prompt(query: str, context: str) -> str:
    return (
        f"<|user|>\n"
        f"Answer the question using this context: {context}\n\n"
        f"Question: {query}<|assistant|>\n"
    )


def make_citation_prompt(query: str, context: str) -> str:
    return (
        f"<|user|>\n"
        f"Answer using ONLY the provided context. For every factual claim, cite the exact source sentence it came from. "
        f"If the context doesn't contain the answer, say so explicitly rather than guessing.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}<|assistant|>\n"
    )


def compute_condition_stats(rows: List[Dict], cond_key: str) -> Dict:
    n = len(rows)
    if n == 0:
        return {}

    scores = [r[cond_key]["trust_score"] for r in rows]
    claims = [r[cond_key]["num_claims"] for r in rows]
    truncations = [r[cond_key]["is_truncated"] for r in rows]

    trusted = sum(1 for r in rows if r[cond_key]["status"] == "Trusted")
    uncertain = sum(1 for r in rows if r[cond_key]["status"] == "Uncertain")
    hallu = sum(1 for r in rows if r[cond_key]["status"] == "Hallucinated")
    truncated_count = sum(1 for t in truncations if t)

    # Hallucination rate excluding truncated answers
    non_truncated_rows = [r for r in rows if not r[cond_key]["is_truncated"]]
    non_trunc_n = len(non_truncated_rows)
    if non_trunc_n > 0:
        non_trunc_hallu = sum(1 for r in non_truncated_rows if r[cond_key]["status"] == "Hallucinated")
        pct_hallu_excl_trunc = round((non_trunc_hallu / non_trunc_n) * 100, 1)
    else:
        pct_hallu_excl_trunc = round((hallu / n) * 100, 1)

    return {
        "mean_trust_score": round(statistics.mean(scores), 2),
        "median_trust_score": round(statistics.median(scores), 2),
        "pct_trusted": round((trusted / n) * 100, 1),
        "pct_uncertain": round((uncertain / n) * 100, 1),
        "pct_hallucinated": round((hallu / n) * 100, 1),
        "pct_hallucinated_excluding_truncated": pct_hallu_excl_trunc,
        "mean_atomic_claims": round(statistics.mean(claims), 2),
        "truncation_rate": round((truncated_count / n) * 100, 1),
        "count_trusted": trusted,
        "count_uncertain": uncertain,
        "count_hallucinated": hallu,
        "count_truncated": truncated_count,
        "total": n
    }


def run_ablation_2x2():
    dataset_path = os.path.join(PROJECT_ROOT, "data", "eval_dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    total_queries = len(eval_data)
    print("=" * 90, flush=True)
    print(f"STARTING PHASE 4: 2x2 CONTROLLED ABLATION STUDY ({total_queries} QUERIES)", flush=True)
    print("Condition A: Baseline Retrieval + Baseline Prompt", flush=True)
    print("Condition B: SBERT Re-ranking   + Baseline Prompt (Isolates Re-Ranking)", flush=True)
    print("Condition C: Baseline Retrieval + Citation Prompt (Isolates Citation Prompting)", flush=True)
    print("Condition D: SBERT Re-ranking   + Citation Prompt (Combined)", flush=True)
    print("Max tokens raised to 110 with automated truncation tracking.", flush=True)
    print("=" * 90, flush=True)

    rows = []
    t_start = time.time()

    for idx, item in enumerate(eval_data, 1):
        qid = item["id"]
        query = item["query"]
        category = categorize_query(item["error_type"])

        # 1. Retrieval
        ret_base = retrieve_baseline(query, top_k=2)
        ret_imp = retrieve_improved(query, candidate_pool_size=10, top_k=2)

        ctx_base = " ".join([p["text"] for p in ret_base])
        ctx_imp = " ".join([p["text"] for p in ret_imp])
        retrieval_identical = ([x["text"] for x in ret_base] == [x["text"] for x in ret_imp])

        # Condition A: Base Retrieval + Base Prompt
        p_a = make_baseline_prompt(query, ctx_base)
        ans_a, trunc_a, tok_a = generate(p_a, max_new_tokens=110, return_meta=True)
        ver_a = verify(query, ans_a, ret_base)

        # Condition B: Imp Retrieval + Base Prompt
        if retrieval_identical:
            ans_b, trunc_b, tok_b = ans_a, trunc_a, tok_a
            ver_b = ver_a
        else:
            p_b = make_baseline_prompt(query, ctx_imp)
            ans_b, trunc_b, tok_b = generate(p_b, max_new_tokens=110, return_meta=True)
            ver_b = verify(query, ans_b, ret_imp)

        # Condition C: Base Retrieval + Citation Prompt
        p_c = make_citation_prompt(query, ctx_base)
        ans_c, trunc_c, tok_c = generate(p_c, max_new_tokens=110, return_meta=True)
        ver_c = verify(query, ans_c, ret_base)

        # Condition D: Imp Retrieval + Citation Prompt
        if retrieval_identical:
            ans_d, trunc_d, tok_d = ans_c, trunc_c, tok_c
            ver_d = ver_c
        else:
            p_d = make_citation_prompt(query, ctx_imp)
            ans_d, trunc_d, tok_d = generate(p_d, max_new_tokens=110, return_meta=True)
            ver_d = verify(query, ans_d, ret_imp)

        row = {
            "id": qid,
            "query": query,
            "category": category,
            "error_type_proxy": item["error_type"],
            "retrieval_identical": retrieval_identical,
            "cond_a": {
                "name": "Base Ret + Base Prompt",
                "answer": ans_a,
                "trust_score": round(ver_a["trust_score"], 2),
                "status": ver_a["status"],
                "num_claims": len(ver_a["claims"]),
                "is_truncated": trunc_a,
                "tokens": tok_a,
                "explanation": ver_a["explanation"]
            },
            "cond_b": {
                "name": "SBERT Re-rank + Base Prompt",
                "answer": ans_b,
                "trust_score": round(ver_b["trust_score"], 2),
                "status": ver_b["status"],
                "num_claims": len(ver_b["claims"]),
                "is_truncated": trunc_b,
                "tokens": tok_b,
                "explanation": ver_b["explanation"]
            },
            "cond_c": {
                "name": "Base Ret + Citation Prompt",
                "answer": ans_c,
                "trust_score": round(ver_c["trust_score"], 2),
                "status": ver_c["status"],
                "num_claims": len(ver_c["claims"]),
                "is_truncated": trunc_c,
                "tokens": tok_c,
                "explanation": ver_c["explanation"]
            },
            "cond_d": {
                "name": "SBERT Re-rank + Citation Prompt",
                "answer": ans_d,
                "trust_score": round(ver_d["trust_score"], 2),
                "status": ver_d["status"],
                "num_claims": len(ver_d["claims"]),
                "is_truncated": trunc_d,
                "tokens": tok_d,
                "explanation": ver_d["explanation"]
            }
        }
        rows.append(row)

        print(
            f"[{idx:02d}/{total_queries}] {qid:<10} | "
            f"A: {ver_a['status'][0]} ({ver_a['trust_score']:4.1f}) | "
            f"B: {ver_b['status'][0]} ({ver_b['trust_score']:4.1f}) | "
            f"C: {ver_c['status'][0]} ({ver_c['trust_score']:4.1f}) | "
            f"D: {ver_d['status'][0]} ({ver_d['trust_score']:4.1f})",
            flush=True
        )

    elapsed = time.time() - t_start
    print("=" * 90, flush=True)
    print(f"2x2 Ablation finished in {elapsed:.1f}s ({elapsed/total_queries:.2f}s/query)", flush=True)

    # Aggregate 2x2 Stats
    stats_a = compute_condition_stats(rows, "cond_a")
    stats_b = compute_condition_stats(rows, "cond_b")
    stats_c = compute_condition_stats(rows, "cond_c")
    stats_d = compute_condition_stats(rows, "cond_d")

    # Category Breakdown
    categories = sorted(list(set(r["category"] for r in rows)))
    category_breakdown = {}
    for cat in categories:
        cat_rows = [r for r in rows if r["category"] == cat]
        category_breakdown[cat] = {
            "sample_size": len(cat_rows),
            "cond_a": compute_condition_stats(cat_rows, "cond_a"),
            "cond_b": compute_condition_stats(cat_rows, "cond_b"),
            "cond_c": compute_condition_stats(cat_rows, "cond_c"),
            "cond_d": compute_condition_stats(cat_rows, "cond_d"),
        }

    # Selected Illustrative Differences
    diffs_rerank = [r for r in rows if r["cond_a"]["status"] != r["cond_b"]["status"]]
    diffs_prompt = [r for r in rows if r["cond_a"]["status"] != r["cond_c"]["status"]]
    diffs_combined = [r for r in rows if r["cond_a"]["status"] != r["cond_d"]["status"]]

    ablation_results = {
        "metadata": {
            "total_queries": total_queries,
            "runtime_seconds": round(elapsed, 1),
            "max_tokens": 110,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "conditions": {
            "cond_a_baseline": stats_a,
            "cond_b_rerank_only": stats_b,
            "cond_c_citation_only": stats_c,
            "cond_d_combined": stats_d
        },
        "category_breakdown": category_breakdown,
        "divergence_counts": {
            "rerank_only_vs_baseline": len(diffs_rerank),
            "citation_only_vs_baseline": len(diffs_prompt),
            "combined_vs_baseline": len(diffs_combined)
        },
        "diff_examples": {
            "rerank_alone": diffs_rerank[:5],
            "citation_alone": diffs_prompt[:5],
            "combined": diffs_combined[:5]
        },
        "all_rows": rows
    }

    # Save to results/rag_comparison.json
    out_dir = os.path.join(PROJECT_ROOT, "results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "rag_comparison.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ablation_results, f, indent=2)
    print(f"\nSaved 2x2 ablation results to: {out_path}", flush=True)

    # Print 2x2 Matrix Table
    print("\n" + "=" * 90, flush=True)
    print("PHASE 4: 2x2 ABLATION MATRIX SUMMARY", flush=True)
    print("=" * 90, flush=True)
    print(f"{'Condition':<32} | {'Mean':<6} | {'Median':<6} | {'%Trust':<7} | {'%Uncert':<7} | {'%Hallu (All)':<12} | {'%Hallu (Excl Trunc)':<18} | {'Mean Claims':<11} | {'Trunc%':<6}", flush=True)
    print("-" * 125, flush=True)
    conds = [
        ("A: Base Ret + Base Prompt", stats_a),
        ("B: SBERT Re-rank + Base Prompt", stats_b),
        ("C: Base Ret + Citation Prompt", stats_c),
        ("D: SBERT Re-rank + Citation Prompt", stats_d),
    ]
    for name, s in conds:
        print(
            f"{name:<32} | {s['mean_trust_score']:<6.1f} | {s['median_trust_score']:<6.1f} | "
            f"{s['pct_trusted']:>5.1f}% | {s['pct_uncertain']:>5.1f}% | "
            f"{s['pct_hallucinated']:>5.1f}%      | {s['pct_hallucinated_excluding_truncated']:>5.1f}%             | "
            f"{s['mean_atomic_claims']:<11.2f} | {s['truncation_rate']:>4.1f}%",
            flush=True
        )
    print("=" * 125, flush=True)

    return ablation_results


if __name__ == "__main__":
    run_ablation_2x2()

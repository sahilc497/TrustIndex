import json
import os
from scipy import stats
# Or compute exact binomial test / McNemar using standard python math
import math

RESULTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "rag_comparison.json"))

with open(RESULTS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = data["all_rows"]
print(f"Loaded {len(rows)} rows from {RESULTS_PATH}")

def mcnemar(rows, key1, key2):
    # Paired 2x2 contingency table for Hallucinated vs Not-Hallucinated
    # Outcome: True if Hallucinated, False otherwise
    # a: Both Hallucinated
    # b: cond1 Hallucinated, cond2 Not-Hallucinated
    # c: cond1 Not-Hallucinated, cond2 Hallucinated
    # d: Both Not-Hallucinated
    a = b = c = d = 0
    flips_1_to_not2 = []
    flips_not1_to_2 = []

    for r in rows:
        h1 = (r[key1]["status"] == "Hallucinated")
        h2 = (r[key2]["status"] == "Hallucinated")

        if h1 and h2:
            a += 1
        elif h1 and not h2:
            b += 1
            flips_1_to_not2.append(r["id"])
        elif not h1 and h2:
            c += 1
            flips_not1_to_2.append(r["id"])
        else:
            d += 1

    n_discordant = b + c
    # Exact two-sided binomial test on discordant pairs
    # under null hypothesis p=0.5
    if n_discordant == 0:
        p_exact = 1.0
        chi2_stat = 0.0
        p_chi2 = 1.0
    else:
        # Binomial test
        # scipy or manual
        try:
            res_binom = stats.binomtest(b, n_discordant, 0.5, alternative="two-sided")
            p_exact = res_binom.pvalue
        except Exception:
            # Fallback manual exact binomial
            # P(X <= min(b,c)) * 2
            k = min(b, c)
            p_exact = min(1.0, 2.0 * sum(math.comb(n_discordant, i) * (0.5**n_discordant) for i in range(k + 1)))

        # McNemar with continuity correction: (|b - c| - 1)^2 / (b + c)
        if abs(b - c) > 0:
            chi2_stat = ((abs(b - c) - 1) ** 2) / (b + c)
            try:
                p_chi2 = 1.0 - stats.chi2.cdf(chi2_stat, df=1)
            except Exception:
                p_chi2 = None
        else:
            chi2_stat = 0.0
            p_chi2 = 1.0

    return {
        "cond1": key1,
        "cond2": key2,
        "both_hallu (a)": a,
        "cond1_hallu_cond2_not (b)": b,
        "cond1_not_cond2_hallu (c)": c,
        "both_not (d)": d,
        "n_discordant (b+c)": n_discordant,
        "chi2_corrected": round(chi2_stat, 4) if chi2_stat is not None else None,
        "p_chi2": round(p_chi2, 4) if p_chi2 is not None else None,
        "p_exact_binomial": round(p_exact, 4),
        "is_significant_05": p_exact < 0.05,
        "flips_1_to_not2": flips_1_to_not2,
        "flips_not1_to_2": flips_not1_to_2
    }

pairs_to_test = [
    ("cond_a", "cond_b", "A vs B (Base vs Re-rank Alone)"),
    ("cond_a", "cond_c", "A vs C (Base vs Citation Alone)"),
    ("cond_a", "cond_d", "A vs D (Base vs Combined)"),
    ("cond_b", "cond_d", "B vs D (Re-rank vs Combined)"),
    ("cond_c", "cond_d", "C vs D (Citation vs Combined)"),
]

print("\n" + "="*80)
print("MCNEMAR PAIRED SIGNIFICANCE TESTS ON HALLUCINATED OUTCOME (N=77)")
print("="*80)

results_summary = {}
for k1, k2, label in pairs_to_test:
    res = mcnemar(rows, k1, k2)
    results_summary[label] = res
    print(f"\n--- {label} ---")
    print(f"  Contingency Table: a={res['both_hallu (a)']}, b={res['cond1_hallu_cond2_not (b)']}, c={res['cond1_not_cond2_hallu (c)']}, d={res['both_not (d)']}")
    print(f"  Discordant Pairs (b+c): {res['n_discordant (b+c)']} (b={res['cond1_hallu_cond2_not (b)']}, c={res['cond1_not_cond2_hallu (c)']})")
    print(f"  Exact Binomial p-value: {res['p_exact_binomial']} | Chi2 (corr): {res['chi2_corrected']} (p={res['p_chi2']})")
    print(f"  Significant at p < 0.05? {res['is_significant_05']}")
    if "A vs C" in label:
        print(f"  A vs C specific flips:")
        print(f"    Flipped Hallucinated -> Not-Hallucinated in C (b): {res['cond1_hallu_cond2_not (b)']} ({res['flips_1_to_not2']})")
        print(f"    Flipped Not-Hallucinated -> Hallucinated in C (c): {res['cond1_not_cond2_hallu (c)']} ({res['flips_not1_to_2']})")

# Category breakdowns with raw counts
print("\n" + "="*80)
print("CATEGORY BREAKDOWN RAW COUNTS & PERCENTAGES")
print("="*80)

for cat_name, cat_data in data["category_breakdown"].items():
    n = cat_data["sample_size"]
    print(f"\nCategory: {cat_name} (n={n})")
    for cond_key, label in [("cond_a", "Cond A"), ("cond_b", "Cond B"), ("cond_c", "Cond C"), ("cond_d", "Cond D")]:
        c_stats = cat_data[cond_key]
        h_cnt = c_stats["count_hallucinated"]
        h_pct = c_stats["pct_hallucinated"]
        t_cnt = c_stats["count_trusted"]
        t_pct = c_stats["pct_trusted"]
        u_cnt = c_stats["count_uncertain"]
        u_pct = c_stats["pct_uncertain"]
        mean_s = c_stats["mean_trust_score"]
        print(f"  {label:<8}: Mean={mean_s:5.1f} | Trust={t_pct:>5.1f}% ({t_cnt}/{n}) | Uncert={u_pct:>5.1f}% ({u_cnt}/{n}) | Hallu={h_pct:>5.1f}% ({h_cnt}/{n})")

# Save detailed stats
out_stats_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "mcnemar_stats.json"))
with open(out_stats_path, "w", encoding="utf-8") as f:
    json.dump(results_summary, f, indent=2)

print(f"\nSaved statistical test details to {out_stats_path}")

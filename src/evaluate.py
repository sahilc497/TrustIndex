"""
Evaluation harness.

Runs the detector on every (correct_answer, hallucinated_answer) pair in
data/eval_dataset.json and reports:
  - overall accuracy (correct answers classified Trusted/Uncertain,
    hallucinated answers classified Hallucinated/Uncertain-with-flag)
  - precision/recall for hallucination detection
  - per-error-type breakdown
  - the full score distribution, saved to results/eval_results.json

Decision rule for this evaluation (binary, for precision/recall purposes):
    predicted_hallucinated = (status == "Hallucinated")
    ground truth: correct_answer -> not hallucinated
                  hallucinated_answer -> hallucinated
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.detector import verify


def load_dataset(path="data/eval_dataset.json"):
    with open(path) as f:
        return json.load(f)


def run_evaluation():
    dataset = load_dataset()

    rows = []
    for item in dataset:
        evidence = [{"doc": item["source_doc"], "text": item["source_passage"]}]

        correct_result = verify(item["query"], item["correct_answer"], evidence)
        hallu_result = verify(item["query"], item["hallucinated_answer"], evidence)

        rows.append({
            "id": item["id"],
            "error_type": item["error_type"],
            "correct_answer": item["correct_answer"],
            "correct_trust_score": correct_result["trust_score"],
            "correct_status": correct_result["status"],
            "hallucinated_answer": item["hallucinated_answer"],
            "hallucinated_trust_score": hallu_result["trust_score"],
            "hallucinated_status": hallu_result["status"],
            "hallucinated_explanation": hallu_result["explanation"],
        })

    return rows


def compute_metrics(rows):
    # binary: is it flagged as Hallucinated?
    tp = sum(1 for r in rows if r["hallucinated_status"] == "Hallucinated")          # correctly caught
    fn = sum(1 for r in rows if r["hallucinated_status"] != "Hallucinated")          # missed hallucination
    fp = sum(1 for r in rows if r["correct_status"] == "Hallucinated")               # false alarm on correct answer
    tn = sum(1 for r in rows if r["correct_status"] != "Hallucinated")               # correctly left alone

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    accuracy = (tp + tn) / (2 * len(rows)) if rows else 0.0

    per_type = {}
    for r in rows:
        et = r["error_type"]
        per_type.setdefault(et, {"total": 0, "caught_strict": 0, "caught_lenient": 0})
        per_type[et]["total"] += 1
        if r["hallucinated_status"] == "Hallucinated":
            per_type[et]["caught_strict"] += 1
        if r["hallucinated_status"] in ("Hallucinated", "Uncertain"):
            per_type[et]["caught_lenient"] += 1

    return {
        "n_pairs": len(rows),
        "true_positives": tp,
        "false_negatives": fn,
        "false_positives": fp,
        "true_negatives": tn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "accuracy": round(accuracy, 3),
        "per_error_type": {
            k: {
                "total": v["total"],
                "caught": v["caught_strict"],
                "catch_rate": round(v["caught_strict"] / v["total"], 3) if v["total"] else 0.0,
                "caught_lenient": v["caught_lenient"],
                "lenient_catch_rate": round(v["caught_lenient"] / v["total"], 3) if v["total"] else 0.0,
            }
            for k, v in sorted(per_type.items())
        },
    }


BASELINE_METRICS = {
    "system": "Baseline (Rule-based only + TF-IDF)",
    "n_pairs": 32,
    "precision": 0.957,
    "recall": 0.688,
    "f1": 0.800,
    "accuracy": 0.828,
    "per_error_type": {
        "numeric_substitution": {"caught": 16, "total": 18, "catch_rate": 0.889},
        "entity_swap": {"caught": 2, "total": 4, "catch_rate": 0.500},
        "negation": {"caught": 3, "total": 6, "catch_rate": 0.500},
        "unsupported_addition": {"caught": 1, "total": 4, "catch_rate": 0.250},
        "date_change": {"caught": 0, "total": 0, "catch_rate": 0.0},
        "causal_distortion": {"caught": 0, "total": 0, "catch_rate": 0.0},
    }
}


def main():
    rows = run_evaluation()
    metrics = compute_metrics(rows)

    os.makedirs("results", exist_ok=True)
    with open("results/eval_results.json", "w") as f:
        json.dump({"metrics": metrics, "rows": rows}, f, indent=2)

    with open("results/eval_results_upgraded.json", "w") as f:
        json.dump({"metrics": metrics, "rows": rows}, f, indent=2)

    # Save ablation comparison
    ablation = {
        "baseline_rule_based": BASELINE_METRICS,
        "upgraded_sbert_nli": {
            "system": "Upgraded (Rule-based + SBERT + RoBERTa-NLI)",
            "n_pairs": metrics["n_pairs"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "accuracy": metrics["accuracy"],
            "per_error_type": metrics["per_error_type"],
        },
    }
    with open("results/ablation_comparison.json", "w") as f:
        json.dump(ablation, f, indent=2)

    print("=" * 75)
    print("TRUST INDEX -- EVALUATION RESULTS & ABLATION COMPARISON")
    print("=" * 75)
    print(f"{'Metric':<25} {'Baseline (Rule-based)':<22} {'Upgraded (SBERT + NLI)':<22}")
    print("-" * 75)
    print(f"{'Pairs evaluated':<25} {BASELINE_METRICS['n_pairs']:<22} {metrics['n_pairs']:<22}")
    print(f"{'Precision':<25} {BASELINE_METRICS['precision']:<22} {metrics['precision']:<22}")
    print(f"{'Recall':<25} {BASELINE_METRICS['recall']:<22} {metrics['recall']:<22}")
    print(f"{'F1 Score':<25} {BASELINE_METRICS['f1']:<22} {metrics['f1']:<22}")
    print(f"{'Overall accuracy':<25} {BASELINE_METRICS['accuracy']:<22} {metrics['accuracy']:<22}")
    print()
    print("Per error-type breakdown (Strict vs. Lenient):")
    print(f"  {'Error Type':<23} {'Strict (Hallu only)':<22} {'Lenient (Hallu or Uncertain)':<25}")
    print("  " + "-" * 70)
    for et, stats in metrics["per_error_type"].items():
        strict_str = f"{stats['caught']:2d}/{stats['total']:2d} ({stats['catch_rate']*100:.0f}%)"
        lenient_str = f"{stats['caught_lenient']:2d}/{stats['total']:2d} ({stats['lenient_catch_rate']*100:.0f}%)"
        print(f"  {et:<23} {strict_str:<22} {lenient_str:<25}")

    print()
    print("False positives (correct answers wrongly flagged as Hallucinated):", metrics['false_positives'])
    print("False negatives (hallucinations missed):", metrics['false_negatives'])
    print()
    print("Full results saved to results/eval_results.json and results/eval_results_upgraded.json")
    print("Ablation comparison saved to results/ablation_comparison.json")


if __name__ == "__main__":
    main()



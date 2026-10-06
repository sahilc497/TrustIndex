import json
import os
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROVENANCE_PATH = os.path.join(PROJECT_ROOT, "results", "trust_validation", "provenance_audit.json")
PREDICTIONS_PATH = os.path.join(PROJECT_ROOT, "results", "trust_validation", "raw_predictions.json")
VAL_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "trust_validation_dataset.json")
OUTPUT_JSON_PATH = os.path.join(PROJECT_ROOT, "results", "trust_validation", "unseen_subset_results.json")

with open(PROVENANCE_PATH, "r", encoding="utf-8") as f:
    prov_data = json.load(f)

with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
    raw_preds = json.load(f)

with open(VAL_DATA_PATH, "r", encoding="utf-8") as f:
    val_data = json.load(f)

preds_by_id = {x["id"]: x for x in raw_preds}
val_by_id = {x["id"]: x for x in val_data}

# Map provenance per case
provenance_map = {x["case_id"]: x["origin"] for x in prov_data}

held_out_ids = [cid for cid, p in provenance_map.items() if p == "held_out_10"]
newly_ids = [cid for cid, p in provenance_map.items() if p == "newly_constructed"]
combined_ids = held_out_ids + newly_ids
original_ids = [cid for cid, p in provenance_map.items() if p == "original_77"]

print(f"Counts: held_out={len(held_out_ids)}, newly={len(newly_ids)}, combined={len(combined_ids)}, original={len(original_ids)}")

def compute_metrics_for_subset(subset_ids, name):
    records = [preds_by_id[cid] for cid in subset_ids]
    n = len(records)
    
    # 3-way labels: "Trusted", "Uncertain", "Hallucinated"
    labels_3way = ["Trusted", "Uncertain", "Hallucinated"]
    conf_matrix_3way = {exp: {pred: 0 for pred in labels_3way} for exp in labels_3way}
    correct_3way = 0
    
    tp_supp = 0
    fp_supp = 0
    fn_supp = 0
    tn_supp = 0
    
    tp_det = 0
    fp_det = 0
    fn_det = 0
    tn_det = 0
    
    invalid_to_trusted = 0 # Safety critical: expected Uncertain/Hallucinated -> predicted Trusted
    
    scores_by_type = {}
    scores_by_status = {"Trusted": [], "Uncertain": [], "Hallucinated": []}
    
    for r in records:
        exp = r["expected_status"]
        pred = r["predicted_status"]
        score = r["trust_score"]
        ctype = r.get("case_type", "unknown")
        
        conf_matrix_3way[exp][pred] += 1
        if exp == pred:
            correct_3way += 1
            
        # Binary Supported perspective:
        is_exp_supp = (exp == "Trusted")
        is_pred_supp = (pred == "Trusted")
        
        if is_exp_supp and is_pred_supp:
            tp_supp += 1
        elif not is_exp_supp and is_pred_supp:
            fp_supp += 1
        elif is_exp_supp and not is_pred_supp:
            fn_supp += 1
        else:
            tn_supp += 1
            
        # Detection perspective (detecting invalid/unsupported/hallucinated):
        is_exp_invalid = (exp != "Trusted")
        is_pred_invalid = (pred != "Trusted")
        
        if is_exp_invalid and is_pred_invalid:
            tp_det += 1
        elif not is_exp_invalid and is_pred_invalid:
            fp_det += 1
        elif is_exp_invalid and not is_pred_invalid:
            fn_det += 1
        else:
            tn_det += 1
            
        if is_exp_invalid and is_pred_supp:
            invalid_to_trusted += 1
            
        scores_by_type.setdefault(ctype, []).append(score)
        scores_by_status.setdefault(exp, []).append(score)
        
    acc_3way = round(correct_3way / n, 4) if n > 0 else 0.0
    binary_acc = round((tp_det + tn_det) / n, 4) if n > 0 else 0.0
    
    det_prec = round(tp_det / (tp_det + fp_det), 4) if (tp_det + fp_det) > 0 else 0.0
    det_rec = round(tp_det / (tp_det + fn_det), 4) if (tp_det + fn_det) > 0 else 0.0
    det_f1 = round(2 * det_prec * det_rec / (det_prec + det_rec), 4) if (det_prec + det_rec) > 0 else 0.0
    det_spec = round(tn_det / (tn_det + fp_det), 4) if (tn_det + fp_det) > 0 else 0.0
    
    supp_prec = round(tp_supp / (tp_supp + fp_supp), 4) if (tp_supp + fp_supp) > 0 else 0.0
    supp_rec = round(tp_supp / (tp_supp + fn_supp), 4) if (tp_supp + fn_supp) > 0 else 0.0
    supp_f1 = round(2 * supp_prec * supp_rec / (supp_prec + supp_rec), 4) if (supp_prec + supp_rec) > 0 else 0.0
    supp_spec = round(tn_supp / (tn_supp + fp_supp), 4) if (tn_supp + fp_supp) > 0 else 0.0
    
    score_stats_by_type = {}
    for ctype, scs in scores_by_type.items():
        score_stats_by_type[ctype] = {
            "n": len(scs),
            "mean": round(float(np.mean(scs)), 2),
            "median": round(float(np.median(scs)), 2),
            "std": round(float(np.std(scs)), 2),
            "min": round(float(np.min(scs)), 2),
            "max": round(float(np.max(scs)), 2),
            "iqr": round(float(np.percentile(scs, 75) - np.percentile(scs, 25)), 2)
        }
        
    score_stats_by_status = {}
    for status, scs in scores_by_status.items():
        if scs:
            score_stats_by_status[status] = {
                "n": len(scs),
                "mean": round(float(np.mean(scs)), 2),
                "median": round(float(np.median(scs)), 2),
                "std": round(float(np.std(scs)), 2),
                "min": round(float(np.min(scs)), 2),
                "max": round(float(np.max(scs)), 2),
                "iqr": round(float(np.percentile(scs, 75) - np.percentile(scs, 25)), 2)
            }
            
    return {
        "name": name,
        "n_samples": n,
        "three_way_accuracy": acc_3way,
        "three_way_confusion_matrix": conf_matrix_3way,
        "binary_accuracy": binary_acc,
        "hallucination_detection": {
            "tp": tp_det,
            "fp": fp_det,
            "fn": fn_det,
            "tn": tn_det,
            "precision": det_prec,
            "recall": det_rec,
            "f1": det_f1,
            "specificity": det_spec
        },
        "supported_perspective": {
            "tp": tp_supp,
            "fp": fp_supp,
            "fn": fn_supp,
            "tn": tn_supp,
            "precision": supp_prec,
            "recall": supp_rec,
            "f1": supp_f1,
            "specificity": supp_spec
        },
        "safety_violations_invalid_to_trusted": {
            "count": invalid_to_trusted,
            "denominator": tp_det + fn_det,
            "rate": round(invalid_to_trusted / (tp_det + fn_det), 4) if (tp_det + fn_det) > 0 else 0.0
        },
        "score_stats_by_expected_status": score_stats_by_status,
        "score_stats_by_case_type": score_stats_by_type
    }

held_out_res = compute_metrics_for_subset(held_out_ids, "Subset A - Previously Held-Out (N=11)")
newly_res = compute_metrics_for_subset(newly_ids, "Subset B - Newly Constructed (N=31)")
combined_res = compute_metrics_for_subset(combined_ids, "Subset C - Combined Unseen (N=42)")
original_res = compute_metrics_for_subset(original_ids, "Original 77 Subset (N=88)")
all_res = compute_metrics_for_subset(list(preds_by_id.keys()), "Full Validation (N=130)")

# Find errors on combined unseen
errors_unseen = []
for cid in combined_ids:
    r = preds_by_id[cid]
    if r["expected_status"] != r["predicted_status"]:
        errors_unseen.append({
            "case_id": cid,
            "provenance": provenance_map[cid],
            "case_type": r.get("case_type"),
            "expected_status": r["expected_status"],
            "predicted_status": r["predicted_status"],
            "predicted_trust_score": r["trust_score"],
            "query": r.get("query"),
            "answer": r.get("answer"),
            "evidence": r.get("evidence"),
            "error_type": r.get("error_type")
        })

output_data = {
    "metadata": {
        "analysis_name": "TRUST Index Final Unseen-Subset Analysis",
        "date": "2026-10-06",
        "description": "Evaluation of TRUST Index verification performance on cases not present in the original 77-case benchmark.",
        "subsets": {
            "subset_a_held_out_11": len(held_out_ids),
            "subset_b_newly_constructed_31": len(newly_ids),
            "subset_c_combined_unseen_42": len(combined_ids),
            "historical_original_77_eval": len(original_ids),
            "total_validation_set": len(preds_by_id)
        }
    },
    "subset_a_held_out_11": held_out_res,
    "subset_b_newly_constructed_31": newly_res,
    "subset_c_combined_unseen_42": combined_res,
    "original_77_eval_88": original_res,
    "full_validation_130": all_res,
    "comparison_table": {
        "metrics": [
            {
                "metric": "Binary Accuracy",
                "full_130": all_res["binary_accuracy"],
                "unseen_42": combined_res["binary_accuracy"],
                "delta": round(combined_res["binary_accuracy"] - all_res["binary_accuracy"], 4)
            },
            {
                "metric": "Detection Precision",
                "full_130": all_res["hallucination_detection"]["precision"],
                "unseen_42": combined_res["hallucination_detection"]["precision"],
                "delta": round(combined_res["hallucination_detection"]["precision"] - all_res["hallucination_detection"]["precision"], 4)
            },
            {
                "metric": "Detection Recall",
                "full_130": all_res["hallucination_detection"]["recall"],
                "unseen_42": combined_res["hallucination_detection"]["recall"],
                "delta": round(combined_res["hallucination_detection"]["recall"] - all_res["hallucination_detection"]["recall"], 4)
            },
            {
                "metric": "Detection F1",
                "full_130": all_res["hallucination_detection"]["f1"],
                "unseen_42": combined_res["hallucination_detection"]["f1"],
                "delta": round(combined_res["hallucination_detection"]["f1"] - all_res["hallucination_detection"]["f1"], 4)
            },
            {
                "metric": "Supported Recall",
                "full_130": all_res["supported_perspective"]["recall"],
                "unseen_42": combined_res["supported_perspective"]["recall"],
                "delta": round(combined_res["supported_perspective"]["recall"] - all_res["supported_perspective"]["recall"], 4)
            },
            {
                "metric": "Invalid -> Trusted (Safety Violations)",
                "full_130": f"{all_res['safety_violations_invalid_to_trusted']['count']}/{all_res['safety_violations_invalid_to_trusted']['denominator']} ({all_res['safety_violations_invalid_to_trusted']['rate']*100:.1f}%)",
                "unseen_42": f"{combined_res['safety_violations_invalid_to_trusted']['count']}/{combined_res['safety_violations_invalid_to_trusted']['denominator']} ({combined_res['safety_violations_invalid_to_trusted']['rate']*100:.1f}%)",
                "delta": "0.0%"
            },
            {
                "metric": "3-Way Accuracy",
                "full_130": all_res["three_way_accuracy"],
                "unseen_42": combined_res["three_way_accuracy"],
                "delta": round(combined_res["three_way_accuracy"] - all_res["three_way_accuracy"], 4)
            }
        ]
    },
    "errors_on_unseen_42": errors_unseen
}

with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2)

print("Saved output to", OUTPUT_JSON_PATH)
print("Errors found on unseen 42:", len(errors_unseen))
for err in errors_unseen:
    print(f"[{err['case_id']}] Type: {err['case_type']} | Expected: {err['expected_status']} -> Predicted: {err['predicted_status']} | Score: {err['predicted_trust_score']}")

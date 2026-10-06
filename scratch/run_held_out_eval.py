import json
import os
import sys

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.detector import verify

def run_held_out_eval():
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "held_out_eval_dataset.json"))
    with open(data_path, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    print(f"Loaded {len(pairs)} held-out entity_swap test pairs.\n" + "="*80)

    results = []
    caught_strict = 0
    caught_lenient = 0
    correct_passed = 0

    for idx, item in enumerate(pairs, 1):
        pid = item["id"]
        doc = item["source_doc"]
        passage = item["source_passage"]
        correct = item["correct_answer"]
        hallucinated = item["hallucinated_answer"]
        explanation = item["error_explanation"]

        evidence = [{"doc": doc, "text": passage}]
        res_corr = verify(item["query"], correct, evidence)
        res_hall = verify(item["query"], hallucinated, evidence)

        corr_trusted = res_corr["status"] == "Trusted"
        if corr_trusted:
            correct_passed += 1

        hall_status = res_hall["status"]
        hall_score = res_hall["trust_score"]
        strict_caught = (hall_status == "Hallucinated")
        lenient_caught = (hall_status in ["Hallucinated", "Uncertain"])

        if strict_caught:
            caught_strict += 1
        if lenient_caught:
            caught_lenient += 1

        print(f"[{idx}/10] ID: {pid}")
        print(f"  Passage:      {passage}")
        print(f"  Hallucinated: {hallucinated}")
        print(f"  Swap detail:  {explanation}")
        print(f"  Result:       Score={hall_score:.1f}, Status={hall_status}")
        for c in res_hall["claims"]:
            print(f"    Claim: \"{c['claim']}\" -> Consensus={c['consensus']:.3f}")
            for e in c.get("evidence", []):
                print(f"      Edge to doc={e['doc']}: Sim={e['similarity']:.3f}, Label={e['label']}, Reason={e.get('reason')}")
        print(f"  Caught? Strict: {strict_caught} | Lenient: {lenient_caught}")
        print("-" * 80)

        results.append({
            "id": pid,
            "source_doc": doc,
            "source_passage": passage,
            "correct_answer": correct,
            "correct_result": {
                "trust_score": res_corr["trust_score"],
                "status": res_corr["status"]
            },
            "hallucinated_answer": hallucinated,
            "hallucinated_result": {
                "trust_score": res_hall["trust_score"],
                "status": res_hall["status"],
                "explanation": res_hall["explanation"],
                "claims": res_hall["claims"]
            },
            "strict_caught": strict_caught,
            "lenient_caught": lenient_caught,
            "error_explanation": explanation
        })

    strict_rate = (caught_strict / len(pairs)) * 100
    lenient_rate = (caught_lenient / len(pairs)) * 100
    corr_rate = (correct_passed / len(pairs)) * 100

    print("=" * 80)
    print("HELD-OUT EVALUATION SUMMARY")
    print(f"Total novel entity_swap pairs: {len(pairs)}")
    print(f"Correct answer pass rate (Trusted): {correct_passed}/{len(pairs)} ({corr_rate:.1f}%)")
    print(f"Strict catch rate (Status == Hallucinated): {caught_strict}/{len(pairs)} ({strict_rate:.1f}%)")
    print(f"Lenient catch rate (Status != Trusted):     {caught_lenient}/{len(pairs)} ({lenient_rate:.1f}%)")
    print("=" * 80)

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "held_out_eval_results.json"))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_pairs": len(pairs),
            "strict_catch_rate": strict_rate,
            "lenient_catch_rate": lenient_rate,
            "strict_caught": caught_strict,
            "lenient_caught": caught_lenient,
            "correct_pass_rate": corr_rate,
            "details": results
        }, f, indent=2)
    print(f"Saved results to {out_path}")

if __name__ == "__main__":
    run_held_out_eval()

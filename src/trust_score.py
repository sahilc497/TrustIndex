"""
Trust Scoring module.

Combines per-claim evidence graph consensus scores into a single overall
Trust Score (0-100) for the full answer, then classifies it.

SCORING METHODOLOGY (explicit, not hand-waved):

Per claim:
    claim_score = (consensus + 1) / 2 * 100        # rescale [-1,1] -> [0,100]

Overall answer score:
    trust_score = min(claim_score for claim in claims)   # weakest-link

WHY WEAKEST-LINK (min) RATHER THAN AVERAGE:
An answer with 3 correct claims and 1 hallucinated claim should NOT score
~75% (which an average would give it) -- it contains a hallucination and
a user relying on it could be misled by that one claim. Trust is not
additive across claims; one contradicted claim should dominate the score.
This is a deliberate design choice and should be validated against the
labeled dataset (see evaluate.py) rather than assumed correct.

CLASSIFICATION THRESHOLDS (initial values, tune empirically):
    >= 80           -> Trusted
    50 - 79         -> Uncertain
    < 50            -> Hallucinated

These thresholds are placeholders. Run evaluate.py against the labeled
dataset and inspect the score distribution for correct vs. hallucinated
answers (e.g. via a precision/recall sweep) to pick better cutoffs.
"""

TRUSTED_THRESHOLD = 80
UNCERTAIN_THRESHOLD = 50


def score_claim(claim_graph: dict) -> float:
    consensus = claim_graph["consensus"]
    return round((consensus + 1) / 2 * 100, 1)


def score_answer(claim_graphs: list) -> dict:
    """
    claim_graphs: list of outputs from evidence_graph.build_claim_graph()
    """
    claim_scores = [score_claim(cg) for cg in claim_graphs]
    trust_score = min(claim_scores) if claim_scores else 0.0

    if trust_score >= TRUSTED_THRESHOLD:
        status = "Trusted"
    elif trust_score >= UNCERTAIN_THRESHOLD:
        status = "Uncertain"
    else:
        status = "Hallucinated"

    # identify the worst (lowest-scoring) claim for the explanation
    worst_idx = claim_scores.index(min(claim_scores)) if claim_scores else None
    worst_claim = claim_graphs[worst_idx] if worst_idx is not None else None

    return {
        "trust_score": trust_score,
        "status": status,
        "per_claim_scores": list(zip([cg["claim"] for cg in claim_graphs], claim_scores)),
        "weakest_claim": worst_claim,
    }

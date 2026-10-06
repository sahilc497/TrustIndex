"""
Evidence Graph module.

Builds a small bipartite graph connecting each claim to each retrieved
evidence passage, with edges labeled ENTAILMENT / CONTRADICTION / NEUTRAL
and weighted by semantic similarity.

GRAPH CONSENSUS ALGORITHM (this is the precise definition promised in
project planning -- not just a diagram):

For a given claim with edges to N evidence passages:
    support_weight   = sum of similarity scores on ENTAILMENT edges
    contradict_weight = sum of similarity scores on CONTRADICTION edges
    neutral_weight    = sum of similarity scores on NEUTRAL edges

    consensus = (support_weight - contradict_weight) /
                (support_weight + contradict_weight + neutral_weight + eps)

    consensus is in [-1, 1]:
        +1  -> all evidence strongly supports the claim
        -1  -> all evidence strongly contradicts the claim
         0  -> mixed / no signal

This is a weighted-vote propagation score, not a black box -- every term
is traceable back to a specific (claim, evidence) edge, which is what
lets the explanation UI say exactly which document(s) drove the score.
"""

from src.similarity import semantic_similarity
from src.contradiction import check_contradiction

EPS = 1e-6


def build_claim_graph(claim: str, evidence_passages: list):
    """
    evidence_passages: list of dicts {"doc": str, "text": str}

    Returns a dict:
        {
          "claim": claim,
          "edges": [ {"doc", "text", "similarity", "label", "reason"}, ... ],
          "consensus": float,
        }
    """
    edges = []
    support_weight = 0.0
    contradict_weight = 0.0
    neutral_weight = 0.0

    for ev in evidence_passages:
        sim = semantic_similarity(claim, ev["text"])
        label, reason = check_contradiction(claim, ev["text"], sim)

        edges.append({
            "doc": ev["doc"],
            "text": ev["text"],
            "similarity": round(sim, 3),
            "label": label,
            "reason": reason,
        })

        if label == "ENTAILMENT":
            support_weight += sim
        elif label == "CONTRADICTION":
            contradict_weight += sim
        else:
            neutral_weight += sim

    denom = support_weight + contradict_weight + neutral_weight + EPS
    consensus = (support_weight - contradict_weight) / denom

    return {
        "claim": claim,
        "edges": edges,
        "consensus": round(consensus, 3),
        "support_weight": round(support_weight, 3),
        "contradict_weight": round(contradict_weight, 3),
        "neutral_weight": round(neutral_weight, 3),
    }

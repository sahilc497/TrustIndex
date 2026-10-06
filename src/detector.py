"""
TRUST Index Detector - main pipeline orchestrator.

This is the single entry point: verify(query, answer, evidence_passages)
runs claim extraction -> evidence graph construction -> trust scoring,
and returns a full explainable result.
"""

from src.claim_extraction import extract_claims
from src.evidence_graph import build_claim_graph
from src.trust_score import score_answer


def verify(query: str, answer: str, evidence_passages: list) -> dict:
    """
    query: the user's question (kept for logging/explanation; not used
           directly in scoring in this MVP)
    answer: the RAG system's generated answer (string)
    evidence_passages: list of {"doc": str, "text": str} retrieved by
           the RAG system (this pipeline does NOT do its own retrieval)

    Returns a dict with trust_score, status, claims, and explanation --
    the shape you'd return from a POST /verify API endpoint.
    """
    claims = extract_claims(answer)
    claim_graphs = [build_claim_graph(c, evidence_passages) for c in claims]
    result = score_answer(claim_graphs)

    explanation = _build_explanation(result)

    return {
        "query": query,
        "answer": answer,
        "trust_score": result["trust_score"],
        "status": result["status"],
        "claims": [
            {
                "claim": cg["claim"],
                "consensus": cg["consensus"],
                "evidence": cg["edges"],
            }
            for cg in claim_graphs
        ],
        "explanation": explanation,
    }


def _build_explanation(result: dict) -> str:
    status = result["status"]
    weakest = result["weakest_claim"]

    if status == "Trusted":
        return "All claims are well supported by retrieved evidence with no contradictions detected."

    if weakest is None:
        return "No claims could be extracted or verified."

    contradicting_edges = [e for e in weakest["edges"] if e["label"] == "CONTRADICTION"]
    if contradicting_edges:
        worst_edge = min(contradicting_edges, key=lambda e: e["similarity"] * -1)
        return (
            f'Claim "{weakest["claim"]}" contradicts evidence from {worst_edge["doc"]}: '
            f'{worst_edge["reason"]}'
        )

    return (
        f'Claim "{weakest["claim"]}" is not strongly supported by any retrieved evidence '
        f"(low consensus score: {weakest['consensus']})."
    )


if __name__ == "__main__":
    evidence = [
        {"doc": "hr_policy_leave.txt", "text": "Employees are entitled to 20 annual paid leaves per calendar year."}
    ]
    result = verify(
        query="How many annual leaves do employees get?",
        answer="Employees are entitled to 30 annual paid leaves per calendar year.",
        evidence_passages=evidence,
    )
    import json
    print(json.dumps(result, indent=2))

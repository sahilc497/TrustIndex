"""
Semantic Similarity module.

Sentence-BERT implementation using sentence-transformers (model "all-MiniLM-L6-v2").
Cached at module load time.
Returns cosine similarity in [0, 1].
"""

from sentence_transformers import SentenceTransformer, util

# Cache model at module load
_SBERT_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_similarity(claim: str, evidence: str) -> float:
    """
    Returns a similarity score in [0, 1] between a claim and a piece of
    evidence text using Sentence-BERT embeddings.
    """
    emb = _SBERT_MODEL.encode([claim, evidence], convert_to_tensor=True)
    score = float(util.cos_sim(emb[0], emb[1]).item())
    return max(0.0, min(1.0, score))


if __name__ == "__main__":
    print(semantic_similarity(
        "Employees are entitled to 30 annual paid leaves per calendar year.",
        "Employees are entitled to 20 annual paid leaves per calendar year."
    ))


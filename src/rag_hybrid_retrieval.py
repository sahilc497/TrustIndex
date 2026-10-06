"""
Hybrid Retrieval module using Reciprocal Rank Fusion (RRF).

Combines:
1. Lexical Keyword Overlap (Condition A / src.rag_baseline)
2. SBERT Dense Semantic Similarity (Condition B / src.rag_improved)

RRF Formula:
    RRF(d) = sum_{m in {lexical, dense}} 1 / (60 + rank_m(d))
where rank_m(d) is 1-indexed rank in list m.
"""

import re
from typing import List, Dict
from src.rag_baseline import load_corpus
from src.similarity import semantic_similarity

RRF_K = 60


def retrieve_hybrid_rrf(query: str, top_k: int = 2) -> List[Dict[str, str]]:
    """
    RRF Hybrid retrieval fusing lexical keyword overlap and SBERT dense similarity.
    Reuses existing ranking logic from baseline and improved RAG pipelines.
    """
    corpus = load_corpus()
    query_tokens = set(re.findall(r"\w+", query.lower()))

    # List 1: Lexical Ranking (same as Condition A)
    lexical_scored = []
    for doc_name, text in corpus:
        text_tokens = set(re.findall(r"\w+", text.lower()))
        overlap = len(query_tokens & text_tokens)
        lexical_scored.append((overlap, doc_name, text))
    lexical_scored.sort(key=lambda x: x[0], reverse=True)

    # List 2: SBERT Dense Ranking (same as Condition B)
    dense_scored = []
    for _, doc_name, text in lexical_scored:
        sim = semantic_similarity(query, text)
        dense_scored.append((sim, doc_name, text))
    dense_scored.sort(key=lambda x: x[0], reverse=True)

    # Reciprocal Rank Fusion (k=60, 1-indexed ranks)
    rrf_scores = {}
    chunk_meta = {}

    for rank, (score, doc_name, text) in enumerate(lexical_scored, 1):
        key = (doc_name, text)
        rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (RRF_K + rank))
        chunk_meta[key] = {"doc": doc_name, "text": text}

    for rank, (score, doc_name, text) in enumerate(dense_scored, 1):
        key = (doc_name, text)
        rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (RRF_K + rank))
        chunk_meta[key] = {"doc": doc_name, "text": text}

    sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for key, score in sorted_chunks[:top_k]:
        results.append({
            "doc": chunk_meta[key]["doc"],
            "text": chunk_meta[key]["text"],
            "rrf_score": round(score, 5)
        })
    return results


if __name__ == "__main__":
    q = "Can unused sick leave be carried forward?"
    res = retrieve_hybrid_rrf(q, top_k=2)
    for i, r in enumerate(res, 1):
        print(f"[{i}] ({r['doc']}, RRF: {r['rrf_score']}): {r['text'][:80]}...")

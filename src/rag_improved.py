"""
Improved RAG pipeline.

Retrieval: Dense SBERT re-ranking over candidate pool of top-10 lexical matches.
Generation: Citation-forced prompt requiring direct source referencing and explicit refusal.
"""

from typing import List, Dict
from src.llm_client import generate
from src.rag_baseline import load_corpus
from src.similarity import semantic_similarity


def retrieve_improved(query: str, candidate_pool_size: int = 10, top_k: int = 2) -> List[Dict[str, str]]:
    """
    Re-ranking retrieval:
    1. Fetches candidate_pool_size candidates via initial keyword match.
    2. Re-ranks candidates using SBERT semantic similarity.
    3. Returns top_k highest scoring passages.
    """
    corpus = load_corpus()
    import re
    query_tokens = set(re.findall(r"\w+", query.lower()))

    # 1. Initial candidate pool
    scored_candidates = []
    for doc_name, text in corpus:
        text_tokens = set(re.findall(r"\w+", text.lower()))
        overlap = len(query_tokens & text_tokens)
        scored_candidates.append((overlap, doc_name, text))

    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    candidates = scored_candidates[:candidate_pool_size]

    # 2. Semantic re-ranking via SBERT
    reranked = []
    for _, doc_name, text in candidates:
        sim = semantic_similarity(query, text)
        reranked.append((sim, doc_name, text))

    reranked.sort(key=lambda x: x[0], reverse=True)

    # 3. Select final top-k
    results = []
    for sim, doc_name, text in reranked[:top_k]:
        results.append({"doc": doc_name, "text": text})
    return results


def query_rag(query: str, k: int = 2) -> Dict:
    """
    Executes improved RAG pipeline for a given query.
    Signature: (query: str, k: int = 2) -> dict with answer and retrieved_passages.
    """
    retrieved = retrieve_improved(query, top_k=k)
    context_str = " ".join([p["text"] for p in retrieved])

    prompt = (
        f"<|user|>\n"
        f"Answer using ONLY the provided context. For every factual claim, cite the exact source sentence it came from. "
        f"If the context doesn't contain the answer, say so explicitly rather than guessing.\n\n"
        f"Context:\n{context_str}\n\n"
        f"Question: {query}<|assistant|>\n"
    )

    answer = generate(prompt, max_new_tokens=35)
    return {
        "query": query,
        "answer": answer,
        "retrieved_passages": retrieved
    }

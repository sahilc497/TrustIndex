"""
Condition E: Hybrid Retrieval (RRF) + Concise Grounded Prompt.

Designed to address:
1. Confound 1: Claim-count inflation from verbose citation forcing.
2. Confound 2: Dense re-ranking harming exact lexical/negation queries.

Interface: (query: str, k: int = 2) -> Dict with "query", "answer", "retrieved_passages".
"""

from typing import Dict, List
from src.rag_hybrid_retrieval import retrieve_hybrid_rrf
from src.llm_client import generate


def make_condition_e_prompt(query: str, context: str) -> str:
    """
    Concise grounded generation prompt.
    Explicitly instructs ONE short sentence, forbids citations/preambles,
    and supplies exact fallback token for non-answerable queries.
    """
    return (
        f"<|user|>\n"
        f"Answer the question in ONE short sentence using only the provided context. "
        f"Do not add preambles, citations, or explanations -- state only the fact. "
        f"If the context does not contain the answer, respond exactly: 'Not stated in context.'\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}<|assistant|>\n"
    )


def query_rag(query: str, k: int = 2) -> Dict:
    """
    Executes Condition E RAG pipeline for a given query.
    Signature: (query: str, k: int = 2) -> dict with answer and retrieved_passages.
    """
    retrieved = retrieve_hybrid_rrf(query, top_k=k)
    context_str = " ".join([p["text"] for p in retrieved])

    prompt = make_condition_e_prompt(query, context_str)
    answer = generate(prompt, max_new_tokens=110)
    return {
        "query": query,
        "answer": answer,
        "retrieved_passages": retrieved
    }


if __name__ == "__main__":
    q = "Can unused sick leave be carried forward?"
    out = query_rag(q, k=2)
    print("Query:", out["query"])
    print("Answer:", out["answer"])
    print("Retrieved Passages:", len(out["retrieved_passages"]))

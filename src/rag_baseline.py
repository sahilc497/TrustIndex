"""
Baseline RAG pipeline.

Retrieval: Naive top-k keyword/token-overlap match over data/*.txt paragraph chunks.
Generation: Standard prompt ("Answer the question using this context: {context}\n\nQuestion: {query}")
"""

import glob
import os
import re
from typing import List, Dict, Tuple
from src.llm_client import generate

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))


def load_corpus() -> List[Tuple[str, str]]:
    """Loads all policy text files from data/ and splits them into paragraph chunks."""
    passages = []
    txt_files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    for fpath in sorted(txt_files):
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
        for chunk in chunks:
            lines = [l.strip() for l in chunk.split("\n") if l.strip()]
            text = " ".join(lines)
            if len(text) > 30:
                passages.append((fname, text))
    return passages


def retrieve_baseline(query: str, top_k: int = 2) -> List[Dict[str, str]]:
    """
    Naive lexical keyword overlap retrieval.
    Counts overlapping lowercase alphanumeric tokens between query and chunk.
    """
    corpus = load_corpus()
    query_tokens = set(re.findall(r"\w+", query.lower()))

    scored = []
    for doc_name, text in corpus:
        text_tokens = set(re.findall(r"\w+", text.lower()))
        overlap = len(query_tokens & text_tokens)
        scored.append((overlap, doc_name, text))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for overlap, doc_name, text in scored[:top_k]:
        results.append({"doc": doc_name, "text": text})
    return results


def query_rag(query: str, k: int = 2) -> Dict:
    """
    Executes baseline RAG pipeline for a given query.
    Signature: (query: str, k: int = 2) -> dict with answer and retrieved_passages.
    """
    retrieved = retrieve_baseline(query, top_k=k)
    context_str = " ".join([p["text"] for p in retrieved])

    prompt = (
        f"<|user|>\n"
        f"Answer the question using this context: {context_str}\n\n"
        f"Question: {query}<|assistant|>\n"
    )

    answer = generate(prompt, max_new_tokens=35)
    return {
        "query": query,
        "answer": answer,
        "retrieved_passages": retrieved
    }

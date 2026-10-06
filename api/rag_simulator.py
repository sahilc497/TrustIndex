"""
RAG Simulator Module.

NOTE: This is a simplified stand-in RAG simulator for local interactive
demonstrations and testing. It uses naive lexical keyword search over the local
text files in data/*.txt and provides curated or extracted responses. It is NOT
a production retrieval or generation system.
"""

import glob
import json
import os
import re
from typing import List, Tuple
from api.schemas import DocumentPassage

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _load_corpus() -> List[Tuple[str, str]]:
    """Loads all text files from data/ and splits them into paragraph passages."""
    passages = []
    txt_files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    for fpath in txt_files:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        # Split into sections or paragraphs
        chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
        for chunk in chunks:
            # Skip mere title headers
            lines = [l.strip() for l in chunk.split("\n") if l.strip()]
            text = " ".join(lines)
            if len(text) > 30:
                passages.append((fname, text))
    return passages


def retrieve_passages(query: str, top_k: int = 2) -> List[DocumentPassage]:
    """
    Naive keyword-overlap retrieval over data/*.txt.
    Ranks passages by lexical overlap with query tokens.
    """
    corpus = _load_corpus()
    query_tokens = set(re.findall(r"\w+", query.lower()))

    scored = []
    for doc_name, text in corpus:
        text_tokens = set(re.findall(r"\w+", text.lower()))
        overlap = len(query_tokens & text_tokens)
        scored.append((overlap, doc_name, text))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for overlap, doc_name, text in scored[:top_k]:
        results.append(DocumentPassage(doc=doc_name, text=text))
    return results


def generate_simulated_answer(
    query: str,
    retrieved: List[DocumentPassage],
    force_hallucination: bool = False
) -> str:
    """
    Produces a simulated generated answer.
    Matches queries from eval_dataset.json if available, or falls back to
    top evidence extraction or synthesis.
    """
    eval_dataset_path = os.path.join(DATA_DIR, "eval_dataset.json")
    if os.path.exists(eval_dataset_path):
        with open(eval_dataset_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)

        q_clean = query.strip().lower().rstrip("?")
        for item in eval_data:
            item_q = item["query"].strip().lower().rstrip("?")
            if q_clean == item_q or q_clean in item_q or item_q in q_clean:
                if force_hallucination:
                    return item["hallucinated_answer"]
                return item["correct_answer"]

    # Fallback heuristic generator:
    if not retrieved:
        return "I could not find any relevant information in the documentation to answer your query."

    first_evidence = retrieved[0].text
    # Pick first sentence from evidence
    sentences = re.split(r"(?<=[.!?])\s+", first_evidence)
    lead_sentence = sentences[0] if sentences else first_evidence

    if force_hallucination:
        # Corrupt numbers if present, or negate
        numbers = re.findall(r"\b\d+\b", lead_sentence)
        if numbers:
            corrupted = lead_sentence.replace(numbers[0], str(int(numbers[0]) + 15), 1)
            return corrupted
        else:
            return f"Contrary to the standard guidelines, {lead_sentence.lower()}"

    return lead_sentence

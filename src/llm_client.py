"""
Pluggable LLM generation module.

Uses the locally cached instruction-tuned model (TinyLlama/TinyLlama-1.1B-Chat-v1.0)
via transformers. Exposes a single `generate(prompt: str, max_new_tokens: int)`
function so the underlying model can be easily substituted or configured with
API keys later.
"""

import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

_MODEL = None
_TOKENIZER = None
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"


def _init_model():
    global _MODEL, _TOKENIZER
    if _MODEL is None:
        torch.set_num_threads(16)
        _TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)
        if _TOKENIZER.pad_token is None:
            _TOKENIZER.pad_token = _TOKENIZER.eos_token
        _MODEL = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float32
        )
        _MODEL.eval()


def clean_generated_answer(raw_text: str) -> str:
    """
    Strips prompt echoes, conversational prefixes, and trailing hallucinations.
    """
    text = raw_text.strip()
    # Strip leading assistant prefix if present
    if text.lower().startswith("answer:"):
        text = text[len("answer:"):].strip()
    elif text.lower().startswith("a:"):
        text = text[len("a:"):].strip()

    # Cut off at stop sequences
    for delimiter in ["\n\n", "\nQuestion:", "\nQ:", "<|user|>", "</s>"]:
        if delimiter in text:
            text = text.split(delimiter)[0].strip()

    # Strip wrapping quotes
    text = text.strip("\"' ")
    return text


DANGLING_TAIL_WORDS = {
    "and", "or", "but", "with", "to", "for", "in", "still", "below",
    "the", "that", "which", "on", "of", "from", "at", "by", "as", "a", "an"
}


def check_is_truncated(text: str, hit_limit: bool) -> bool:
    """
    Determines if text was truncated mid-sentence.
    """
    if not text:
        return False
    t = text.strip()
    # If it hit token limit and didn't end with sentence-terminating punctuation
    if hit_limit and t[-1] not in ".!?\"'":
        return True
    # Check if last word is a dangling preposition or conjunction
    words = t.split()
    if words:
        last_word = words[-1].lower().rstrip(".,;:!?'\"")
        if last_word in DANGLING_TAIL_WORDS:
            return True
    return False


def generate(prompt: str, max_new_tokens: int = 110, return_meta: bool = False):
    """
    Pluggable generation entrypoint with expanded token limit and truncation detection.
    If return_meta is True, returns (clean_text, is_truncated, token_count).
    Otherwise returns clean_text.
    """
    _init_model()
    inputs = _TOKENIZER(prompt, return_tensors="pt")
    with torch.no_grad():
        out = _MODEL.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=_TOKENIZER.eos_token_id,
        )
    num_tokens = out[0].shape[0] - inputs.input_ids.shape[1]
    hit_limit = (num_tokens >= max_new_tokens)
    raw = _TOKENIZER.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    clean = clean_generated_answer(raw)
    is_trunc = check_is_truncated(clean, hit_limit)

    if return_meta:
        return clean, is_trunc, num_tokens
    return clean

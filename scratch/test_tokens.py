import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
from src.rag_improved import retrieve_improved
from src.llm_client import _init_model, clean_generated_answer
import src.llm_client as lc

lc._init_model()

queries = [
    "How much advance notice is required to schedule meetings outside core hours?", # wfh_018
]

for q in queries:
    retrieved = retrieve_improved(q, top_k=2)
    context_str = " ".join([p["text"] for p in retrieved])
    prompt = (
        f"<|user|>\n"
        f"Answer using ONLY the provided context. For every factual claim, cite the exact source sentence it came from. "
        f"If the context doesn't contain the answer, say so explicitly rather than guessing.\n\n"
        f"Context:\n{context_str}\n\n"
        f"Question: {q}<|assistant|>\n"
    )
    inputs = lc._TOKENIZER(prompt, return_tensors="pt")
    with torch.no_grad():
        out = lc._MODEL.generate(
            **inputs,
            max_new_tokens=110,
            do_sample=False,
            pad_token_id=lc._TOKENIZER.eos_token_id
        )
    num_gen_tokens = out[0].shape[0] - inputs.input_ids.shape[1]
    raw = lc._TOKENIZER.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    ans = clean_generated_answer(raw)
    print("="*70)
    print("Q:", q)
    print("Tokens generated:", num_gen_tokens)
    print("Clean Answer:", repr(ans))
    ends_punct = ans[-1] in ".!?\"'" if ans else False
    print("Properly terminated?", ends_punct)

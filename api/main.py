import os
import sys
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Ensure workspace root is in python path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from src.detector import verify
from api.schemas import (
    VerifyRequest,
    VerifyResponse,
    SimulateRagRequest,
    SimulateRagResponse,
    DocumentPassage,
)
from api.rag_simulator import retrieve_passages, generate_simulated_answer

app = FastAPI(
    title="TRUST Index API",
    description="Explainable Verification Layer for Retrieval-Augmented Generation (RAG) systems",
    version="1.0.0",
)

# Enable CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/verify", response_model=VerifyResponse)
def verify_endpoint(req: VerifyRequest):
    """
    Verifies a generated answer against retrieved evidence passages.
    Returns trust score, classification status, per-claim evidence graph, and explanation.
    """
    evidence_dicts = [p.model_dump() for p in req.retrieved_documents]
    result = verify(
        query=req.query,
        answer=req.answer,
        evidence_passages=evidence_dicts,
    )
    return result


@app.post("/verify/batch", response_model=List[VerifyResponse])
def verify_batch_endpoint(reqs: List[VerifyRequest]):
    """
    Batch verification endpoint for running multiple queries and answers concurrently.
    """
    results = []
    for req in reqs:
        evidence_dicts = [p.model_dump() for p in req.retrieved_documents]
        res = verify(
            query=req.query,
            answer=req.answer,
            evidence_passages=evidence_dicts,
        )
        results.append(res)
    return results


@app.post("/simulate-rag", response_model=SimulateRagResponse)
def simulate_rag_endpoint(req: SimulateRagRequest):
    """
    Stand-in RAG simulation:
    1. Lexical retrieval over local policy knowledge base.
    2. Simulated answer generation (or corrupted/hallucinated answer if requested).
    3. Immediate execution of TRUST Index verification layer.
    """
    retrieved = retrieve_passages(req.query, top_k=2)
    generated_answer = generate_simulated_answer(
        query=req.query,
        retrieved=retrieved,
        force_hallucination=req.force_hallucination or False,
    )

    evidence_dicts = [p.model_dump() for p in retrieved]
    verification_result = verify(
        query=req.query,
        answer=generated_answer,
        evidence_passages=evidence_dicts,
    )

    return SimulateRagResponse(
        query=req.query,
        generated_answer=generated_answer,
        retrieved_documents=retrieved,
        verification=verification_result,
    )

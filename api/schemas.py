from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class DocumentPassage(BaseModel):
    doc: str = Field(..., description="Document source name or identifier")
    text: str = Field(..., description="Content of the retrieved evidence passage")


class VerifyRequest(BaseModel):
    query: str = Field(..., description="The user question submitted to the RAG system")
    answer: str = Field(..., description="The generated response to be verified")
    retrieved_documents: List[DocumentPassage] = Field(
        ..., description="List of evidence passages retrieved by the RAG system"
    )


class EvidenceEdge(BaseModel):
    doc: str
    text: str
    similarity: float
    label: str
    reason: str


class ClaimItem(BaseModel):
    claim: str
    consensus: float
    evidence: List[EvidenceEdge]


class VerifyResponse(BaseModel):
    query: str
    answer: str
    trust_score: float
    status: Literal["Trusted", "Uncertain", "Hallucinated"]
    claims: List[ClaimItem]
    explanation: str


class SimulateRagRequest(BaseModel):
    query: str = Field(..., description="User question to process through simulated RAG")
    force_hallucination: Optional[bool] = Field(
        False, description="Optionally force a hallucinated answer for demo purposes"
    )


class SimulateRagResponse(BaseModel):
    query: str
    generated_answer: str
    retrieved_documents: List[DocumentPassage]
    verification: VerifyResponse

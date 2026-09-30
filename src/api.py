from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .generate import generate_answer
from .verify_citations import verify_answer

app = FastAPI(title="NimbusDesk RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


class Citation(BaseModel):
    citation_number: int
    source_file: str
    heading: str


class VerificationResult(BaseModel):
    sentence: str
    citation: int
    source: str
    verdict: str
    overlap_ratio: float | None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Citation]
    verification: list[VerificationResult]
    retrieval_time_seconds: float
    generation_time_seconds: float


@app.post("/v1/ask", response_model=AskResponse)
def ask(request: AskRequest):
    """
    Accepts a question, runs it through the full RAG pipeline,
    and returns a grounded answer with sources and citation verification.
    """
    answer, chunks, retrieval_time, generation_time = generate_answer(request.question)

    sources = [
        Citation(
            citation_number=i + 1,
            source_file=chunk["source_file"],
            heading=chunk["heading"]
        )
        for i, chunk in enumerate(chunks)
    ]

    verification_raw = verify_answer(answer, chunks) if chunks else []
    verification = [
        VerificationResult(
            sentence=v["sentence"],
            citation=v["citation"],
            source=v["source"],
            verdict=v["verdict"],
            overlap_ratio=v["overlap_ratio"]
        )
        for v in verification_raw
    ]

    return AskResponse(
        question=request.question,
        answer=answer,
        sources=sources,
        verification=verification,
        retrieval_time_seconds=round(retrieval_time, 2),
        generation_time_seconds=round(generation_time, 2)
    )


@app.get("/v1/health")
def health():
    """
    Simple endpoint to check the API is running.
    """
    return {"status": "ok"}
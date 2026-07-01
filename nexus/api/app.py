"""FastAPI application for the Nexus REST API.

Endpoints:

- ``GET /`` — web UI (HTML)
- ``GET /api/health`` — health check
- ``GET /api/agents`` — list registered agents
- ``POST /api/interpret`` — ask Nexus a question
- ``POST /api/validate`` — validate a claim
- ``POST /api/index`` — index a document
- ``GET /api/search?q=...`` — search the RAG index
- ``POST /api/biokit`` — run a BioKit program
- ``POST /api/report`` — generate a report
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from nexus.providers.dummy import DummyProvider
from nexus.sdk import Nexus
from nexus.web.templates import HTML

app = FastAPI(
    title="Nexus Ω — Biological Interpretation Intelligence",
    description="AI-native scientific operating system for biology.",
    version="0.1.0",
)

# Process-global Nexus instance. Set via set_nexus() before serving.
_NEXUS: Nexus | None = None


def set_nexus(nexus: Nexus) -> None:
    """Set the process-global Nexus instance."""
    global _NEXUS
    _NEXUS = nexus


def get_nexus() -> Nexus:
    """Get the process-global Nexus instance, creating a default if missing."""
    global _NEXUS
    if _NEXUS is None:
        _NEXUS = Nexus(provider=DummyProvider())
    return _NEXUS


# ── Request / response models ────────────────────────────────────────


class InterpretRequest(BaseModel):
    question: str = Field(..., description="The question to ask.")
    agent: str = Field("literature", description="Agent to use.")
    context: dict[str, Any] = Field(default_factory=dict)


class InterpretResponse(BaseModel):
    answer: str
    confidence: float
    provider_model: str | None
    citations: list[str]
    contradictions: list[str]
    recommended_next_step: str | None
    evidence_ids: list[str]


class ValidateRequest(BaseModel):
    claim: str
    context: dict[str, Any] = Field(default_factory=dict)


class IndexRequest(BaseModel):
    source_uri: str
    title: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    results: list[dict[str, Any]]


class BiokitRequest(BaseModel):
    program: str
    inputs: dict[str, Any]


class BiokitResponse(BaseModel):
    program: str
    outputs: dict[str, Any]
    fingerprint: str


class ReportRequest(BaseModel):
    title: str = "Nexus report"
    questions: list[str] = Field(default_factory=list)


class ReportResponse(BaseModel):
    title: str
    markdown: str
    n_sections: int


class HealthResponse(BaseModel):
    status: str
    version: str
    agents: list[str]
    provider: str


# ── Routes ────────────────────────────────────────────────────────────


@app.get("/")
def root() -> HTMLResponse:
    """Serve the minimal web UI."""
    return HTMLResponse(HTML)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    nx = get_nexus()
    from nexus import __version__

    return HealthResponse(
        status="ok",
        version=__version__,
        agents=nx.list_agents(),
        provider=nx.provider.name,
    )


@app.get("/api/agents", response_model=list[str])
def agents() -> list[str]:
    return get_nexus().list_agents()


@app.post("/api/interpret", response_model=InterpretResponse)
def interpret(req: InterpretRequest) -> InterpretResponse:
    nx = get_nexus()
    try:
        result = nx.interpret(req.question, agent=req.agent, context=req.context or None)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return InterpretResponse(
        answer=result.answer,
        confidence=result.confidence.value,
        provider_model=result.provider_model,
        citations=result.citations,
        contradictions=result.contradictions,
        recommended_next_step=result.recommended_next_step,
        evidence_ids=result.evidence_ids,
    )


@app.post("/api/validate", response_model=InterpretResponse)
def validate(req: ValidateRequest) -> InterpretResponse:
    nx = get_nexus()
    try:
        result = nx.interpret(req.claim, agent="validation", context=req.context or None)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return InterpretResponse(
        answer=result.answer,
        confidence=result.confidence.value,
        provider_model=result.provider_model,
        citations=result.citations,
        contradictions=result.contradictions,
        recommended_next_step=result.recommended_next_step,
        evidence_ids=result.evidence_ids,
    )


@app.post("/api/index")
def index(req: IndexRequest) -> dict[str, Any]:
    nx = get_nexus()
    nx.index_text(req.source_uri, req.title, req.content, req.metadata)
    return {"status": "indexed", "title": req.title, "uri": req.source_uri}


@app.get("/api/search", response_model=SearchResponse)
def search(q: str, limit: int = 5) -> SearchResponse:
    nx = get_nexus()
    results = nx.retriever.retrieve(q, limit=limit)
    return SearchResponse(
        query=q,
        results=[r.to_dict() for r in results],
    )


@app.post("/api/biokit", response_model=BiokitResponse)
def run_biokit(req: BiokitRequest) -> BiokitResponse:
    nx = get_nexus()
    try:
        output = nx.run_biokit(req.program, req.inputs)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return BiokitResponse(
        program=output.program,
        outputs=output.outputs,
        fingerprint=output.fingerprint,
    )


@app.post("/api/report", response_model=ReportResponse)
def generate_report(req: ReportRequest) -> ReportResponse:
    nx = get_nexus()
    interpretations = []
    for q in req.questions:
        try:
            interpretations.append(nx.interpret(q, agent="literature"))
        except Exception:
            continue
    report = nx.generate_report(req.title, interpretations)
    return ReportResponse(
        title=report.title,
        markdown=report.to_markdown(),
        n_sections=len(report.sections),
    )


__all__ = ["app", "get_nexus", "set_nexus"]

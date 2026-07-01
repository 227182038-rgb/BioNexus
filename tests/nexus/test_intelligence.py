"""Tests for nexus.intelligence and nexus.agents."""

from __future__ import annotations

import pytest
from nexus.agents.base import AgentContext
from nexus.agents.experiment_agent import ExperimentAgent
from nexus.agents.literature_agent import LiteratureAgent
from nexus.agents.report_agent import ReportAgent
from nexus.agents.validation_agent import ValidationAgent
from nexus.core.engine import Engine
from nexus.intelligence.explanation import ExplanationModule
from nexus.intelligence.hypothesis import HypothesisModule
from nexus.intelligence.interpretation import InterpretationModule
from nexus.intelligence.reasoning import ReasoningModule
from nexus.intelligence.validation import ValidationModule
from nexus.providers.dummy import DummyProvider
from nexus.rag.indexing import Indexer, InMemoryIndex
from nexus.rag.retrieval import Retriever


@pytest.fixture
def setup(engine: Engine, provider: DummyProvider) -> tuple[Engine, DummyProvider, Retriever]:
    """Engine with a populated RAG retriever."""
    idx = InMemoryIndex()
    indexer = Indexer(idx)
    indexer.add_text(
        "pubmed:1",
        "BRCA1 function",
        "BRCA1 is a tumor suppressor involved in DNA repair.",
    )
    indexer.add_text(
        "pubmed:2",
        "TP53 mutations",
        "TP53 is frequently mutated in cancer; however, BRCA1 mutations are tissue-specific.",
    )
    retriever = Retriever(idx)
    return engine, provider, retriever


# ── Intelligence modules ──────────────────────────────────────────────


class TestInterpretationModule:
    @pytest.mark.asyncio
    async def test_run_returns_interpretation(
        self, setup: tuple[Engine, DummyProvider, Retriever]
    ) -> None:
        engine, provider, _ = setup
        module = InterpretationModule(engine=engine, provider=provider)
        result = await module.run("What does this mean?", context={"biokit_program": "blastp"})
        assert result.answer == "Test answer."
        assert result.confidence.value > 0.0
        assert result.recommended_next_step is not None


class TestValidationModule:
    @pytest.mark.asyncio
    async def test_run_with_contradictions(
        self, setup: tuple[Engine, DummyProvider, Retriever]
    ) -> None:
        engine, provider, _ = setup
        module = ValidationModule(engine=engine, provider=provider)
        result = await module.run(
            "validate this",
            context={
                "claim_statement": "BRCA1 is unrelated to DNA repair.",
                "retrieved_knowledge": [
                    "BRCA1 is involved in DNA repair.",
                    "However, BRCA1 expression varies by tissue.",
                ],
            },
        )
        # Should surface the contradiction ("However" triggers it).
        assert len(result.contradictions) >= 1


class TestReasoningModule:
    @pytest.mark.asyncio
    async def test_run_returns_alternatives(
        self, setup: tuple[Engine, DummyProvider, Retriever]
    ) -> None:
        engine, provider, _ = setup
        module = ReasoningModule(engine=engine, provider=provider)
        result = await module.run(
            "Explain the mechanism",
            context={
                "claim_ids": ["c1"],
                "claim_statements": ["BRCA1 repairs DNA."],
            },
        )
        assert len(result.alternatives) >= 1
        assert len(result.contradictions) >= 1


class TestHypothesisModule:
    @pytest.mark.asyncio
    async def test_low_confidence(self, setup: tuple[Engine, DummyProvider, Retriever]) -> None:
        engine, provider, _ = setup
        module = HypothesisModule(engine=engine, provider=provider)
        result = await module.run("Generate a hypothesis", context={"claim_ids": ["c1"]})
        # Hypotheses are speculative — confidence should be low.
        assert result.confidence.value <= 0.5


class TestExplanationModule:
    @pytest.mark.asyncio
    async def test_audience_levels(self, setup: tuple[Engine, DummyProvider, Retriever]) -> None:
        engine, provider, _ = setup
        module = ExplanationModule(engine=engine, provider=provider)
        for audience in ("beginner", "undergraduate", "graduate", "researcher", "expert"):
            result = await module.run(
                "Explain BRCA1",
                context={
                    "claim_statement": "BRCA1 is a tumor suppressor.",
                    "audience": audience,
                },
            )
            assert result.answer == "Test answer."

    @pytest.mark.asyncio
    async def test_invalid_audience_falls_back(
        self, setup: tuple[Engine, DummyProvider, Retriever]
    ) -> None:
        engine, provider, _ = setup
        module = ExplanationModule(engine=engine, provider=provider)
        result = await module.run(
            "Explain",
            context={"claim_statement": "x", "audience": "invalid_audience"},
        )
        assert result.answer == "Test answer."


# ── Agents ────────────────────────────────────────────────────────────


@pytest.fixture
def agent_ctx(setup: tuple[Engine, DummyProvider, Retriever]) -> AgentContext:
    engine, provider, retriever = setup
    return AgentContext(engine=engine, provider=provider, retriever=retriever)


class TestLiteratureAgent:
    @pytest.mark.asyncio
    async def test_run_returns_interpretation_with_citations(self, agent_ctx: AgentContext) -> None:
        agent = LiteratureAgent(agent_ctx)
        result = await agent.run("Tell me about BRCA1")
        assert result.answer == "Test answer."
        # Should have retrieved documents as citations.
        assert isinstance(result.citations, list)


class TestValidationAgent:
    @pytest.mark.asyncio
    async def test_run(self, agent_ctx: AgentContext) -> None:
        agent = ValidationAgent(agent_ctx)
        result = await agent.run(
            "validate",
            context={"claim_statement": "BRCA1 has no role in DNA repair."},
        )
        assert result.answer == "Test answer."


class TestExperimentAgent:
    @pytest.mark.asyncio
    async def test_run_returns_next_step(self, agent_ctx: AgentContext) -> None:
        agent = ExperimentAgent(agent_ctx)
        result = await agent.run("design an experiment")
        assert result.recommended_next_step is not None
        assert "experiment" in result.recommended_next_step.lower()


class TestReportAgent:
    @pytest.mark.asyncio
    async def test_run_with_prior_interpretations(self, agent_ctx: AgentContext) -> None:
        from nexus.core.types import Confidence, EvidenceClass, Interpretation

        prior = Interpretation(
            answer="Prior finding.",
            confidence=Confidence(value=0.8, evidence_class=EvidenceClass.COMPUTATIONAL),
            citations=["pubmed:1"],
        )
        agent = ReportAgent(agent_ctx)
        result = await agent.run(
            "Summarize",
            context={"previous_interpretations": [prior]},
        )
        assert result.answer == "Test answer."
        assert "pubmed:1" in result.citations

    @pytest.mark.asyncio
    async def test_run_without_prior(self, agent_ctx: AgentContext) -> None:
        agent = ReportAgent(agent_ctx)
        result = await agent.run("Summarize", context={})
        assert result.answer == "Test answer."

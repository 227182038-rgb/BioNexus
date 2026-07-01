"""Tests for nexus.memory and nexus.reports."""

from __future__ import annotations

from pathlib import Path

import pytest
from nexus.core.engine import Engine
from nexus.core.types import (
    Claim,
    Confidence,
    EvidenceClass,
    Interpretation,
    Provenance,
    Uncertainty,
)
from nexus.memory.conversation_memory import ConversationMemory
from nexus.memory.project_memory import ProjectMemory
from nexus.memory.research_memory import ResearchMemory
from nexus.providers.base import Role
from nexus.reports.generator import ReportGenerator


@pytest.fixture
def engine_with_claim(engine: Engine) -> Engine:
    """Engine with one AI-assisted claim registered."""
    from nexus.core.types import Evidence

    ev = Evidence(
        source_class=EvidenceClass.COMPUTATIONAL,
        source_uri="model://test",
        content="x",
        fingerprint="",
    )
    engine.register_evidence(ev)
    claim = Claim(
        statement="BRCA1 is a tumor suppressor.",
        evidence_ids=[ev.id],
        provenance=Provenance(hops=[ev.id]),
        uncertainty=Uncertainty(epistemic=0.3),
        confidence=Confidence(value=0.8, evidence_class=EvidenceClass.COMPUTATIONAL),
        is_deterministic=False,
        tags=frozenset({"cancer", "dna_repair"}),
    )
    engine.register_claim(claim)
    return engine


class TestResearchMemory:
    def test_recall_by_tag(self, engine_with_claim: Engine) -> None:
        mem = ResearchMemory(engine=engine_with_claim)
        results = mem.recall_by_tag("cancer")
        assert len(results) == 1
        assert "BRCA1" in results[0].statement

    def test_recall_by_text(self, engine_with_claim: Engine) -> None:
        mem = ResearchMemory(engine=engine_with_claim)
        results = mem.recall_by_text("brca1")
        assert len(results) == 1

    def test_statistics(self, engine_with_claim: Engine) -> None:
        mem = ResearchMemory(engine=engine_with_claim)
        stats = mem.statistics()
        assert stats["total_claims"] == 1
        assert "cancer" in stats["tags"]


class TestConversationMemory:
    def test_add_and_retrieve_turns(self) -> None:
        mem = ConversationMemory()
        mem.add_user_turn("hello")
        mem.add_assistant_turn("hi")
        assert len(mem.turns) == 2

    def test_max_turns_eviction(self) -> None:
        mem = ConversationMemory(max_turns=3)
        mem.add_user_turn("a")
        mem.add_assistant_turn("b")
        mem.add_user_turn("c")
        mem.add_assistant_turn("d")
        assert len(mem.turns) == 3

    def test_to_messages(self) -> None:
        mem = ConversationMemory(system_prompt="You are helpful.")
        mem.add_user_turn("hello")
        messages = mem.to_messages()
        assert messages[0].role == Role.SYSTEM
        assert messages[0].content == "You are helpful."
        assert messages[1].role == Role.USER

    def test_recent_summary(self) -> None:
        mem = ConversationMemory()
        mem.add_user_turn("hello")
        summary = mem.recent_summary()
        assert "hello" in summary


class TestProjectMemory:
    def test_save_and_load(self, tmp_path: Path) -> None:
        proj = ProjectMemory(name="test project")
        proj.set_setting("provider", "openai")
        proj.add_artifact("results", "file:///tmp/results.json")
        path = proj.save(tmp_path / "proj.json")

        loaded = ProjectMemory.load(path)
        assert loaded.name == "test project"
        assert loaded.get_setting("provider") == "openai"
        assert loaded.get_artifact("results") == "file:///tmp/results.json"

    def test_record_event(self) -> None:
        proj = ProjectMemory(name="test")
        proj.record_event("test_event", {"key": "value"})
        assert len(proj.history) == 1
        assert proj.history[0]["type"] == "test_event"

    def test_get_setting_with_default(self) -> None:
        proj = ProjectMemory(name="test")
        assert proj.get_setting("missing", "default") == "default"


class TestReportGenerator:
    def test_generate_markdown(self) -> None:
        from nexus.core.types import Confidence, EvidenceClass

        interp = Interpretation(
            answer="BRCA1 is involved in DNA repair.",
            confidence=Confidence(value=0.85, evidence_class=EvidenceClass.COMPUTATIONAL),
            citations=["pubmed:1", "pubmed:2"],
            recommended_next_step="Run a complementation assay.",
        )
        gen = ReportGenerator()
        report = gen.generate("Test report", [interp])
        md = report.to_markdown()
        assert "BRCA1" in md
        assert "pubmed:1" in md
        assert "Test report" in md

    def test_generate_text(self) -> None:
        from nexus.core.types import Confidence, EvidenceClass

        interp = Interpretation(
            answer="Test answer.",
            confidence=Confidence(value=0.5, evidence_class=EvidenceClass.COMPUTATIONAL),
        )
        gen = ReportGenerator()
        report = gen.generate("Title", [interp])
        text = report.to_text()
        assert "Title" in text
        assert "Test answer" in text

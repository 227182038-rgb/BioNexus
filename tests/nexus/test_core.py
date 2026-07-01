"""Tests for nexus.core — types, BioKit boundary, engine invariants."""

from __future__ import annotations

import pytest
from nexus.core.biokit import InProcessBioKit
from nexus.core.engine import (
    AIClaimMissingUncertaintyError,
    DeterministicClaimHasUncertaintyError,
    Engine,
    ProvenanceIncompleteError,
)
from nexus.core.types import (
    Claim,
    ClaimEdge,
    ClaimEdgeType,
    Confidence,
    Evidence,
    EvidenceClass,
    Provenance,
    Uncertainty,
)

# ── Types ─────────────────────────────────────────────────────────────


class TestUncertainty:
    def test_total_with_no_components(self) -> None:
        u = Uncertainty()
        assert u.total() == 0.0

    def test_total_with_components(self) -> None:
        u = Uncertainty(aleatoric=0.3, epistemic=0.4)
        # RSS: sqrt(0.09 + 0.16) = sqrt(0.25) = 0.5
        assert abs(u.total() - 0.5) < 1e-6

    def test_total_clamped_to_one(self) -> None:
        u = Uncertainty(aleatoric=1.0, epistemic=1.0, model_form=1.0)
        assert u.total() == 1.0

    def test_calibration_drift_increases_total(self) -> None:
        u_no_drift = Uncertainty(aleatoric=0.5)
        u_drift = Uncertainty(aleatoric=0.5, calibration_drift=0.5)
        assert u_drift.total() > u_no_drift.total()

    def test_invalid_value_rejected(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Uncertainty(aleatoric=1.5)


class TestEvidence:
    def test_fingerprint_is_stable(self) -> None:
        ev1 = Evidence(
            source_class=EvidenceClass.PUBLICATION,
            source_uri="doi:10.1/test",
            content="hello",
            fingerprint="",
        )
        # The validator computes fingerprint if empty.
        assert ev1.fingerprint != ""
        ev2 = Evidence(
            source_class=EvidenceClass.PUBLICATION,
            source_uri="doi:10.1/test",
            content="hello",
            fingerprint="",
        )
        assert ev1.fingerprint == ev2.fingerprint

    def test_different_content_different_fingerprint(self) -> None:
        ev1 = Evidence(
            source_class=EvidenceClass.PUBLICATION,
            source_uri="doi:10.1/test",
            content="hello",
            fingerprint="",
        )
        ev2 = Evidence(
            source_class=EvidenceClass.PUBLICATION,
            source_uri="doi:10.1/test",
            content="world",
            fingerprint="",
        )
        assert ev1.fingerprint != ev2.fingerprint


# ── BioKit boundary ───────────────────────────────────────────────────


class EchoProgram:
    """A trivial deterministic BioKit program for tests."""

    name = "echo"

    def run(self, inputs: dict[str, object]) -> dict[str, object]:
        return {"echo": inputs.get("message", "")}


class TestInProcessBioKit:
    def test_register_and_run(self) -> None:
        bk = InProcessBioKit()
        bk.register_program(EchoProgram())
        out = bk.run("echo", {"message": "hello"})
        assert out.program == "echo"
        assert out.outputs == {"echo": "hello"}
        assert out.deterministic is True

    def test_unknown_program_raises(self) -> None:
        bk = InProcessBioKit()
        with pytest.raises(KeyError):
            bk.run("nonexistent", {})

    def test_duplicate_register_raises(self) -> None:
        bk = InProcessBioKit()
        bk.register_program(EchoProgram())
        with pytest.raises(ValueError):
            bk.register_program(EchoProgram())

    def test_list_programs(self) -> None:
        bk = InProcessBioKit()
        bk.register_program(EchoProgram())
        assert "echo" in bk.list_programs()

    def test_output_fingerprint_stable(self) -> None:
        bk = InProcessBioKit()
        bk.register_program(EchoProgram())
        out1 = bk.run("echo", {"message": "hello"})
        out2 = bk.run("echo", {"message": "hello"})
        assert out1.fingerprint == out2.fingerprint

    def test_output_fingerprint_differs_for_different_inputs(self) -> None:
        bk = InProcessBioKit()
        bk.register_program(EchoProgram())
        out1 = bk.run("echo", {"message": "hello"})
        out2 = bk.run("echo", {"message": "world"})
        assert out1.fingerprint != out2.fingerprint

    def test_as_evidence_is_deterministic(self) -> None:
        bk = InProcessBioKit()
        bk.register_program(EchoProgram())
        out = bk.run("echo", {"message": "hello"})
        ev = out.as_evidence()
        assert ev.source_class == EvidenceClass.DETERMINISTIC


# ── Engine invariants ─────────────────────────────────────────────────


class TestEngine:
    def test_register_evidence_idempotent_on_fingerprint(self, engine: Engine) -> None:
        ev = Evidence(
            source_class=EvidenceClass.PUBLICATION,
            source_uri="doi:10.1/x",
            content="content",
            fingerprint="",
        )
        engine.register_evidence(ev)
        engine.register_evidence(ev)  # idempotent
        assert len(engine.evidence_ledger.entries) == 1

    def test_register_deterministic_claim(self, engine: Engine) -> None:
        bk = engine.biokit
        assert bk is not None
        bk.register_program(EchoProgram())
        output = bk.run("echo", {"message": "test"})
        claim = engine.register_biokit_claim(
            statement="The echo program returned 'test'.",
            biokit_output=output,
        )
        assert claim.is_deterministic is True
        assert claim.uncertainty is None
        assert claim.confidence.value == 1.0
        assert claim.confidence.evidence_class == EvidenceClass.DETERMINISTIC

    def test_deterministic_claim_with_uncertainty_rejected(self, engine: Engine) -> None:
        ev = Evidence(
            source_class=EvidenceClass.DETERMINISTIC,
            source_uri="biokit://test",
            content="test",
            fingerprint="",
        )
        engine.register_evidence(ev)
        claim = Claim(
            statement="test",
            evidence_ids=[ev.id],
            provenance=Provenance(hops=[ev.id]),
            uncertainty=Uncertainty(aleatoric=0.1),
            confidence=Confidence(value=1.0, evidence_class=EvidenceClass.DETERMINISTIC),
            is_deterministic=True,
        )
        with pytest.raises(DeterministicClaimHasUncertaintyError):
            engine.register_claim(claim)

    def test_ai_claim_without_uncertainty_rejected(self, engine: Engine) -> None:
        ev = Evidence(
            source_class=EvidenceClass.COMPUTATIONAL,
            source_uri="model://test",
            content="test",
            fingerprint="",
        )
        engine.register_evidence(ev)
        claim = Claim(
            statement="AI says so",
            evidence_ids=[ev.id],
            provenance=Provenance(hops=[ev.id]),
            uncertainty=None,
            confidence=Confidence(value=0.5, evidence_class=EvidenceClass.COMPUTATIONAL),
            is_deterministic=False,
        )
        with pytest.raises(AIClaimMissingUncertaintyError):
            engine.register_claim(claim)

    def test_claim_with_unknown_evidence_rejected(self, engine: Engine) -> None:
        claim = Claim(
            statement="x",
            evidence_ids=["nonexistent"],
            provenance=Provenance(hops=[]),
            confidence=Confidence(value=0.5, evidence_class=EvidenceClass.COMPUTATIONAL),
            is_deterministic=False,
            uncertainty=Uncertainty(epistemic=0.5),
        )
        with pytest.raises(ProvenanceIncompleteError):
            engine.register_claim(claim)

    def test_self_referential_provenance_rejected(self, engine: Engine) -> None:
        from nexus.core.engine import CyclicProvenanceError

        ev = Evidence(
            source_class=EvidenceClass.COMPUTATIONAL,
            source_uri="model://test",
            content="x",
            fingerprint="",
        )
        engine.register_evidence(ev)
        claim_id = "cl_test"
        claim = Claim(
            id=claim_id,
            statement="x",
            evidence_ids=[ev.id],
            provenance=Provenance(hops=[ev.id, claim_id]),  # self-reference
            confidence=Confidence(value=0.5, evidence_class=EvidenceClass.COMPUTATIONAL),
            is_deterministic=False,
            uncertainty=Uncertainty(epistemic=0.5),
        )
        with pytest.raises(CyclicProvenanceError):
            engine.register_claim(claim)

    def test_register_edge_and_query_neighbors(self, engine: Engine) -> None:
        bk = engine.biokit
        assert bk is not None
        bk.register_program(EchoProgram())
        out = bk.run("echo", {"message": "a"})
        c1 = engine.register_biokit_claim("claim 1", out)
        out2 = bk.run("echo", {"message": "b"})
        c2 = engine.register_biokit_claim("claim 2", out2)
        engine.register_edge(
            ClaimEdge(
                source_claim_id=c2.id,
                target_claim_id=c1.id,
                edge_type=ClaimEdgeType.CONTRADICTS,
            )
        )
        contradictions = engine.claims_contradicting(c1.id)
        assert any(c.id == c2.id for c in contradictions)

    def test_gate_evaluation(self, engine: Engine) -> None:
        from nexus.core.types import GateName

        result = engine.evaluate_gate(
            gate=GateName.CALIBRATION,
            subject_id="model_1",
            metric_value=0.92,
            threshold=0.90,
        )
        assert result.passed is True
        assert engine.gate_passed("model_1", GateName.CALIBRATION)

    def test_run_biokit_registers_evidence(self, engine: Engine) -> None:
        bk = engine.biokit
        assert bk is not None
        bk.register_program(EchoProgram())
        engine.run_biokit("echo", {"message": "registered"})
        assert len(engine.evidence_ledger.entries) == 1

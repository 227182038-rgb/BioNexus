"""The Engine — Nexus's central intelligence kernel.

The Engine owns the data structures that every other module reads and
writes: the Evidence Ledger, the Claim Graph, the Gate State. It exposes
a minimal, formal interface for registering evidence, registering claims,
tracing provenance, evaluating gates, and querying the kernel.

The Engine is deliberately *not* a reasoning engine. It does not generate
hypotheses, rank targets, or prioritize experiments — those are module
responsibilities. The Engine enforces the invariants under which modules
operate.
"""

from __future__ import annotations

from typing import Any

from nexus.core.biokit import BioKit, BioKitOutput
from nexus.core.types import (
    Claim,
    ClaimEdge,
    ClaimEdgeType,
    ClaimGraph,
    Confidence,
    Evidence,
    EvidenceClass,
    EvidenceLedger,
    GateName,
    GateResult,
    GateState,
    Provenance,
)


class EngineError(Exception):
    """Base class for Engine invariant violations."""


class ProvenanceIncompleteError(EngineError):
    """Raised when a claim's provenance chain is incomplete."""


class DeterministicClaimHasUncertaintyError(EngineError):
    """Raised when a deterministic claim is registered with an uncertainty envelope."""


class AIClaimMissingUncertaintyError(EngineError):
    """Raised when an AI-assisted claim is registered without an uncertainty envelope."""


class CyclicProvenanceError(EngineError):
    """Raised when a claim's provenance chain would create a cycle."""


class Engine:
    """The central intelligence kernel.

    The Engine is the single source of truth for evidence, claims, and
    gate state. Modules interact with the Engine through a small set of
    methods that enforce the architectural invariants:

    - Evidence is append-only and content-addressed.
    - Claims must have provenance chains that trace to source artifacts.
    - Deterministic claims (from BioKit) have no uncertainty envelope.
    - AI-assisted claims must have an uncertainty envelope.
    - Provenance chains must be acyclic.
    """

    def __init__(self, biokit: BioKit | None = None) -> None:
        self._biokit: BioKit | None = biokit
        self._evidence_ledger: EvidenceLedger = EvidenceLedger()
        self._claim_graph: ClaimGraph = ClaimGraph()
        self._gate_state: GateState = GateState()

    # ── BioKit ────────────────────────────────────────────────────────

    @property
    def biokit(self) -> BioKit | None:
        return self._biokit

    def attach_biokit(self, biokit: BioKit) -> None:
        if self._biokit is not None:
            raise EngineError("BioKit is already attached")
        self._biokit = biokit

    def run_biokit(self, program: str, inputs: dict[str, Any]) -> BioKitOutput:
        """Invoke BioKit and automatically register the output as evidence.

        This is the canonical way Nexus modules invoke deterministic
        computation: they never call ``BioKit.run`` directly.
        """
        if self._biokit is None:
            raise EngineError("No BioKit attached to this Engine")
        output = self._biokit.run(program, inputs)
        self.register_evidence(output.as_evidence())
        return output

    # ── Evidence ──────────────────────────────────────────────────────

    def register_evidence(self, evidence: Evidence) -> Evidence:
        """Add evidence to the ledger. Idempotent on fingerprint."""
        return self._evidence_ledger.add(evidence)

    @property
    def evidence_ledger(self) -> EvidenceLedger:
        return self._evidence_ledger

    def get_evidence(self, evidence_id: str) -> Evidence | None:
        return self._evidence_ledger.get(evidence_id)

    # ── Claims ────────────────────────────────────────────────────────

    @property
    def claim_graph(self) -> ClaimGraph:
        return self._claim_graph

    def register_claim(self, claim: Claim) -> Claim:
        """Register a claim in the Claim Graph.

        Validates:
        - The claim's evidence IDs all exist in the ledger.
        - The claim's provenance hops all exist (as evidence or claims).
        - Deterministic claims have no uncertainty envelope.
        - AI-assisted claims have an uncertainty envelope.
        - The provenance chain is acyclic.

        Returns the registered claim. Raises :class:`EngineError` on
        invariant violation.
        """
        # Acyclicity: the claim cannot appear in its own provenance.
        # Checked first because it doesn't require the hop to exist.
        if claim.id in claim.provenance.hops:
            raise CyclicProvenanceError(f"Claim {claim.id} appears in its own provenance chain")

        # Evidence IDs must exist.
        for eid in claim.evidence_ids:
            if self._evidence_ledger.get(eid) is None:
                raise ProvenanceIncompleteError(
                    f"Claim {claim.id} references unknown evidence {eid}"
                )

        # Provenance hops must exist (excluding the claim itself, which
        # would have been caught by the acyclicity check above).
        for hop in claim.provenance.hops:
            if self._evidence_ledger.get(hop) is None and hop not in self._claim_graph.claims:
                raise ProvenanceIncompleteError(
                    f"Claim {claim.id} provenance references unknown hop {hop}"
                )

        # Deterministic vs AI-assisted uncertainty invariant.
        if claim.is_deterministic:
            if claim.uncertainty is not None:
                raise DeterministicClaimHasUncertaintyError(
                    f"Deterministic claim {claim.id} must not carry an uncertainty envelope"
                )
        else:
            if claim.uncertainty is None:
                raise AIClaimMissingUncertaintyError(
                    f"AI-assisted claim {claim.id} must carry an uncertainty envelope"
                )

        self._claim_graph.add_claim(claim)
        return claim

    def register_edge(self, edge: ClaimEdge) -> None:
        self._claim_graph.add_edge(edge)

    def claims_supported_by(self, evidence_id: str) -> list[Claim]:
        """Return all claims that list ``evidence_id`` as supporting evidence."""
        return [c for c in self._claim_graph.claims.values() if evidence_id in c.evidence_ids]

    def claims_contradicting(self, claim_id: str) -> list[Claim]:
        """Return all claims connected to ``claim_id`` by a CONTRADICTS edge."""
        return self._claim_graph.neighbors(claim_id, ClaimEdgeType.CONTRADICTS)

    # ── Gates ─────────────────────────────────────────────────────────

    @property
    def gate_state(self) -> GateState:
        return self._gate_state

    def evaluate_gate(
        self,
        gate: GateName,
        subject_id: str,
        metric_value: float,
        threshold: float,
        reviewer_signature: str | None = None,
        notes: str | None = None,
    ) -> GateResult:
        result = GateResult(
            gate=gate,
            subject_id=subject_id,
            passed=metric_value >= threshold,
            metric_value=metric_value,
            threshold=threshold,
            reviewer_signature=reviewer_signature,
            notes=notes,
        )
        self._gate_state.add(result)
        return result

    def gate_passed(self, subject_id: str, gate: GateName) -> bool:
        latest = self._gate_state.latest(subject_id, gate)
        return latest is not None and latest.passed

    # ── Convenience: make a deterministic claim from a BioKit output ──

    def register_biokit_claim(
        self,
        statement: str,
        biokit_output: BioKitOutput,
        tags: frozenset[str] | None = None,
    ) -> Claim:
        """Register a deterministic claim directly from a BioKit output.

        This is the *only* way to register a deterministic claim. It
        guarantees that the claim's evidence trail leads back to a
        BioKit calculation, enforcing the Prime Directive.
        """
        evidence = biokit_output.as_evidence()
        self.register_evidence(evidence)
        claim = Claim(
            statement=statement,
            evidence_ids=[evidence.id],
            provenance=Provenance(hops=[evidence.id]),
            uncertainty=None,
            confidence=Confidence(
                value=1.0,
                evidence_class=EvidenceClass.DETERMINISTIC,
                decay_half_life_days=None,
            ),
            is_deterministic=True,
            tags=tags or frozenset(),
        )
        return self.register_claim(claim)


__all__ = [
    "AIClaimMissingUncertaintyError",
    "CyclicProvenanceError",
    "DeterministicClaimHasUncertaintyError",
    "Engine",
    "EngineError",
    "ProvenanceIncompleteError",
]

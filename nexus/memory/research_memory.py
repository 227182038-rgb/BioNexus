"""Research memory — long-term memory of claims, evidence, and facts.

Research memory is backed by the Engine's Claim Graph and Evidence
Ledger. This module provides a higher-level query interface: it
remembers facts by tag, supports semantic search over claim
statements (via the RAG retriever if available), and tracks which
claims have been superseded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nexus.core.engine import Engine
from nexus.core.types import Claim, ClaimEdgeType


@dataclass
class ResearchMemory:
    """Long-term research memory backed by the Engine.

    The ResearchMemory does not duplicate the Engine's state; it
    provides convenience views and queries on top of it.
    """

    engine: Engine
    _tags_index: dict[str, set[str]] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        self._tags_index.clear()
        for cid, claim in self.engine.claim_graph.claims.items():
            for tag in claim.tags:
                self._tags_index.setdefault(tag, set()).add(cid)

    def remember(self, claim: Claim) -> Claim:
        """Register a claim in research memory (via the Engine)."""
        registered = self.engine.register_claim(claim)
        for tag in registered.tags:
            self._tags_index.setdefault(tag, set()).add(registered.id)
        return registered

    def recall_by_tag(self, tag: str) -> list[Claim]:
        """Return all claims with the given tag."""
        cids = self._tags_index.get(tag, set())
        return [
            self.engine.claim_graph.claims[cid]
            for cid in cids
            if cid in self.engine.claim_graph.claims
        ]

    def recall_by_text(self, substring: str) -> list[Claim]:
        """Return all claims whose statement contains the substring (case-insensitive)."""
        sub = substring.lower()
        return [c for c in self.engine.claim_graph.claims.values() if sub in c.statement.lower()]

    def supersede(self, old_id: str, new_claim: Claim, rationale: str) -> Claim:
        """Register ``new_claim`` as superseding ``old_id``."""
        registered = self.remember(new_claim)
        from nexus.core.types import ClaimEdge

        self.engine.register_edge(
            ClaimEdge(
                source_claim_id=registered.id,
                target_claim_id=old_id,
                edge_type=ClaimEdgeType.SUPERSEDES,
                rationale=rationale,
            )
        )
        return registered

    def statistics(self) -> dict[str, Any]:
        cg = self.engine.claim_graph
        return {
            "total_claims": len(cg.claims),
            "total_edges": len(cg.edges),
            "total_evidence": len(self.engine.evidence_ledger.entries),
            "tags": {t: len(ids) for t, ids in self._tags_index.items()},
        }


__all__ = ["ResearchMemory"]

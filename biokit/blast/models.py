"""BLAST data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HSP:
    """A single high-scoring pair."""

    query_id: str
    subject_id: str
    query_start: int
    query_end: int
    subject_start: int
    subject_end: int
    query_seq: str = ""
    subject_seq: str = ""
    midline: str = ""
    score: float = 0.0
    evalue: float = 0.0
    identity: int = 0
    positives: int = 0
    gaps: int = 0
    alignment_length: int = 0

    @property
    def percent_identity(self) -> float:
        """Percent identity in [0, 100]."""
        if self.alignment_length == 0:
            return 0.0
        return 100.0 * self.identity / self.alignment_length


@dataclass(frozen=True)
class BlastHit:
    """A subject sequence with one or more HSPs."""

    subject_id: str
    subject_title: str = ""
    subject_length: int = 0
    hsps: list[HSP] = field(default_factory=list)

    @property
    def best_evalue(self) -> float:
        """Lowest E-value across all HSPs."""
        return min((h.evalue for h in self.hsps), default=float("inf"))

    @property
    def best_score(self) -> float:
        """Highest bit score across all HSPs."""
        return max((h.score for h in self.hsps), default=0.0)


@dataclass(frozen=True)
class BlastRecord:
    """All hits for a single query."""

    query_id: str
    query_length: int = 0
    hits: list[BlastHit] = field(default_factory=list)


__all__ = ["HSP", "BlastHit", "BlastRecord"]

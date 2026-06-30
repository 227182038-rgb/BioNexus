"""CRISPR data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GuideRNA:
    """A candidate sgRNA."""

    spacer: str
    pam: str
    strand: str
    position: int
    gc: float
    score: float = 0.0
    off_targets: list[OffTarget] = field(default_factory=list)


@dataclass(frozen=True)
class OffTarget:
    """An off-target site for a guide RNA."""

    sequence: str
    position: int
    strand: str
    mismatches: int


__all__ = ["GuideRNA", "OffTarget"]

"""Primer candidate dataclass."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrimerCandidate:
    """A candidate primer with computed properties."""

    sequence: str
    start: int
    end: int
    strand: str
    tm: float
    gc: float
    self_comp: int
    gc_clamp: int
    score: float = 0.0


__all__ = ["PrimerCandidate"]

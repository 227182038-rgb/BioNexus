"""Alignment result dataclass."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AlignmentResult:
    """Result of a pairwise alignment.

    Attributes
    ----------
    score : float
        Alignment score.
    aligned_seq1 : str
        First aligned sequence (with gaps).
    aligned_seq2 : str
        Second aligned sequence (with gaps).
    matches : int
        Number of identical positions.
    mismatches : int
        Number of mismatching positions.
    gaps : int
        Number of gap characters in the alignment.
    """

    score: float
    aligned_seq1: str
    aligned_seq2: str
    matches: int
    mismatches: int
    gaps: int

    @property
    def identity(self) -> float:
        """Percentage identity (0–100)."""
        if not self.aligned_seq1:
            return 0.0
        return 100.0 * self.matches / len(self.aligned_seq1)

    @property
    def length(self) -> int:
        """Alignment length (including gaps)."""
        return len(self.aligned_seq1)


__all__ = ["AlignmentResult"]

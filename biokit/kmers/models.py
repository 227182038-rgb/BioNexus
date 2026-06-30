"""K-mer data model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Kmer:
    """A k-mer and its frequency."""

    sequence: str
    count: int

    @property
    def length(self) -> int:
        """K-mer length."""
        return len(self.sequence)


__all__ = ["Kmer"]

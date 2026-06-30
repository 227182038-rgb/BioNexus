"""Codon data model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Codon:
    """A codon and its observed frequency."""

    sequence: str
    amino_acid: str
    count: int = 0

    @property
    def is_stop(self) -> bool:
        """True if this is a stop codon."""
        return self.amino_acid == "*"

    @property
    def is_start(self) -> bool:
        """True if this is the canonical start codon (ATG)."""
        return self.sequence == "ATG"


__all__ = ["Codon"]

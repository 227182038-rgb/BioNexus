"""ORF data model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ORF:
    """An open reading frame.

    Attributes
    ----------
    start : int
        0-based start position of the start codon.
    end : int
        0-based end position (exclusive) of the stop codon.
    frame : int
        Reading frame (1, 2, or 3).
    strand : str
        ``"+"`` or ``"-"``.
    nucleotide_sequence : str
        Nucleotide sequence of the ORF (including stop codon).
    protein_sequence : str
        Translated protein (without stop codon).
    """

    start: int
    end: int
    frame: int
    strand: str
    nucleotide_sequence: str
    protein_sequence: str

    @property
    def length(self) -> int:
        """ORF length in nucleotides."""
        return len(self.nucleotide_sequence)

    @property
    def amino_acid_length(self) -> int:
        """Protein length."""
        return len(self.protein_sequence)


__all__ = ["ORF"]

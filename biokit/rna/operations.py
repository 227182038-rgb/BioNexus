"""RNA-specific operations: transcription, reverse transcription, complement."""

from __future__ import annotations

from biokit.sequence.dna import DNA
from biokit.sequence.rna import RNA
from biokit.sequence.validation import validate_dna, validate_rna


def transcribe(dna: str) -> str:
    """Transcribe DNA to mRNA (T → U).

    Examples
    --------
    >>> transcribe("ATGGCAGGTGACCCGTGA")
    'AUGGCAGGUGACCCGUGA'
    """
    validate_dna(dna)
    return dna.upper().replace("T", "U")


def reverse_transcribe(rna: str) -> str:
    """Reverse-transcribe RNA to DNA (U → T).

    Examples
    --------
    >>> reverse_transcribe("AUGGCAGGUGACCCGUGA")
    'ATGGCAGGTGACCCGTGA'
    """
    validate_rna(rna)
    return rna.upper().replace("U", "T")


def complement(sequence: str) -> str:
    """Return the complement of a DNA or RNA sequence."""
    if "U" in sequence.upper():
        return RNA(sequence).complement().sequence
    return DNA(sequence).complement().sequence


def gc_rna(rna: str) -> float:
    """GC fraction of an RNA sequence."""
    from biokit.statistics.sequence_stats import gc_fraction

    return gc_fraction(rna)


__all__ = ["complement", "gc_rna", "reverse_transcribe", "transcribe"]

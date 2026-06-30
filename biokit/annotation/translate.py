"""CDS translation helper (delegates to biokit.translation.Translator)."""

from __future__ import annotations

from biokit.translation.translator import Translator


def translate_cds(sequence: str, frame: int = 1, stop_at_stop: bool = True) -> str:
    """Translate a CDS nucleotide sequence to a protein.

    Examples
    --------
    >>> translate_cds("ATGGCAGGTGACCCGTGA")
    'MAGDP'
    """
    return Translator().translate(sequence, frame=frame, stop_at_stop=stop_at_stop)


__all__ = ["translate_cds"]

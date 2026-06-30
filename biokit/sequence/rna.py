"""RNA sequence type."""

from __future__ import annotations

from biokit.constants import RNA_ALPHABET, RNA_COMPLEMENT
from biokit.sequence.sequence import BioSequence


class RNA(BioSequence):
    """An RNA sequence.

    Parameters
    ----------
    sequence : str
        RNA sequence (case-insensitive, will be upper-cased).
    id : str, optional
        Sequence identifier.
    description : str, optional
        Human-readable description.

    Examples
    --------
    >>> rna = RNA("AUGGCAGGUGACCCGUGA")
    >>> rna.length
    18
    >>> rna.reverse_transcribe().sequence
    'ATGGCAGGTGACCCGTGA'
    """

    alphabet = RNA_ALPHABET

    def complement(self) -> RNA:
        """Return the complement (not reversed) of this RNA sequence.

        Examples
        --------
        >>> RNA("AUGC").complement().sequence
        'UACG'
        """
        return RNA(
            "".join(RNA_COMPLEMENT[b] for b in self._sequence),
            id=self._id,
            description=self._description,
        )

    def reverse_complement(self) -> RNA:
        """Return the reverse complement of this RNA sequence."""
        return RNA(
            "".join(RNA_COMPLEMENT[b] for b in reversed(self._sequence)),
            id=self._id,
            description=self._description,
        )

    def reverse_transcribe(self) -> DNA:
        """Reverse-transcribe RNA to DNA (U → T).

        Examples
        --------
        >>> rna = RNA("AUGGCAGGUGACCCGUGA")
        >>> rna.reverse_transcribe().sequence
        'ATGGCAGGTGACCCGTGA'
        """
        from biokit.sequence.dna import DNA

        return DNA(self._sequence.replace("U", "T"), id=self._id, description=self._description)


__all__ = ["RNA"]

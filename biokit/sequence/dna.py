"""DNA sequence type."""

from __future__ import annotations

from biokit.constants import DNA_ALPHABET, DNA_COMPLEMENT
from biokit.sequence.sequence import BioSequence


class DNA(BioSequence):
    """A DNA sequence.

    Parameters
    ----------
    sequence : str
        DNA sequence (case-insensitive, will be upper-cased).
    id : str, optional
        Sequence identifier.
    description : str, optional
        Human-readable description.

    Examples
    --------
    >>> dna = DNA("ATGGCAGGTGACCCGTGA")
    >>> dna.length
    18
    >>> dna.gc_content
    0.5555555555555556
    >>> str(dna.reverse_complement())
    'TCACGGGTCACCTGCCAT'
    """

    alphabet = DNA_ALPHABET

    def complement(self) -> DNA:
        """Return the complement (not reversed) of this sequence.

        Examples
        --------
        >>> DNA("ATGC").complement().sequence
        'TACG'
        """
        return DNA(
            "".join(DNA_COMPLEMENT[b] for b in self._sequence),
            id=self._id,
            description=self._description,
        )

    def reverse_complement(self) -> DNA:
        """Return the reverse complement of this sequence.

        Examples
        --------
        >>> DNA("ATGC").reverse_complement().sequence
        'GCAT'
        """
        return DNA(
            "".join(DNA_COMPLEMENT[b] for b in reversed(self._sequence)),
            id=self._id,
            description=self._description,
        )

    def transcribe(self) -> RNA:
        """Transcribe DNA to mRNA (T → U).

        Examples
        --------
        >>> dna = DNA("ATGGCAGGTGACCCGTGA")
        >>> dna.transcribe().sequence
        'AUGGCAGGUGACCCGUGA'
        """
        from biokit.sequence.rna import RNA

        return RNA(self._sequence.replace("T", "U"), id=self._id, description=self._description)

    def translate(self, frame: int = 1) -> Protein:
        """Translate DNA to a protein sequence.

        Parameters
        ----------
        frame : int, optional
            Reading frame (1, 2, or 3), default 1.

        Examples
        --------
        >>> dna = DNA("ATGGCAGGTGACCCGTGA")
        >>> dna.translate().sequence
        'MAGDP'
        """
        from biokit.constants import STANDARD_GENETIC_CODE
        from biokit.sequence.protein import Protein

        if frame not in (1, 2, 3):
            raise ValueError(f"frame must be 1, 2, or 3, got {frame}")
        peptide: list[str] = []
        for i in range(frame - 1, len(self._sequence) - 2, 3):
            codon = self._sequence[i : i + 3]
            if len(codon) < 3:
                break
            aa = STANDARD_GENETIC_CODE.get(codon, "X")
            if aa == "*":
                break
            peptide.append(aa)
        return Protein("".join(peptide), id=self._id, description=self._description)


__all__ = ["DNA"]

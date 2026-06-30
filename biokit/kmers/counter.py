"""K-mer counter."""

from __future__ import annotations

from collections import Counter

from biokit.kmers.models import Kmer


class KmerCounter:
    """Count k-mers in nucleotide sequences.

    Examples
    --------
    >>> counter = KmerCounter()
    >>> kmers = counter.count("ATGCAT", k=3)
    >>> len(kmers)
    2
    >>> kmers[0].sequence
    'ATG'
    """

    def count(self, sequence: str, k: int) -> list[Kmer]:
        """Count k-mers in ``sequence``.

        Parameters
        ----------
        sequence : str
            Nucleotide sequence.
        k : int
            K-mer size (must be ≥ 1).

        Returns
        -------
        list[Kmer]
            K-mers sorted by sequence, with counts.
        """
        if k <= 0:
            raise ValueError("k must be positive")
        seq = sequence.upper()
        if k > len(seq):
            return []
        counts = Counter(seq[i : i + k] for i in range(len(seq) - k + 1))
        return [Kmer(sequence=s, count=c) for s, c in sorted(counts.items())]

    def count_with_positions(self, sequence: str, k: int) -> dict[str, list[int]]:
        """Return k-mers with all positions where they occur.

        Returns
        -------
        dict[str, list[int]]
            K-mer → list of 0-based start positions.
        """
        if k <= 0:
            raise ValueError("k must be positive")
        seq = sequence.upper()
        positions: dict[str, list[int]] = {}
        for i in range(len(seq) - k + 1):
            kmer = seq[i : i + k]
            positions.setdefault(kmer, []).append(i)
        return positions


__all__ = ["KmerCounter"]

"""Motif finder."""

from __future__ import annotations

from biokit.motifs.models import Motif


class MotifFinder:
    """Find motifs in sequences.

    Examples
    --------
    >>> finder = MotifFinder()
    >>> motif = finder.find("ATGCATGCATGC", "ATGC")
    >>> motif.count
    3
    """

    def find(self, sequence: str, motif: str) -> Motif:
        """Find all occurrences of ``motif`` in ``sequence``.

        Parameters
        ----------
        sequence : str
            Sequence to search.
        motif : str
            Motif to find.

        Returns
        -------
        Motif
            The motif with all match positions.
        """
        seq = sequence.upper()
        m = motif.upper()
        positions: list[int] = []
        start = 0
        while True:
            idx = seq.find(m, start)
            if idx < 0:
                break
            positions.append(idx)
            start = idx + 1
        return Motif(sequence=motif, positions=positions)

    def find_all(self, sequence: str, motifs: list[str]) -> list[Motif]:
        """Find multiple motifs."""
        return [self.find(sequence, m) for m in motifs]


__all__ = ["MotifFinder"]

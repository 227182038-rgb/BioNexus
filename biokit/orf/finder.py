"""Six-frame ORF finder."""

from __future__ import annotations

from collections.abc import Iterator

from biokit.constants import STANDARD_GENETIC_CODE, START_CODON, STOP_CODONS
from biokit.orf.models import ORF
from biokit.sequence.dna import DNA


class ORFFinder:
    """Find open reading frames in six frames.

    Parameters
    ----------
    minimum_length : int, optional
        Minimum ORF length in nucleotides (default 30).

    Examples
    --------
    >>> finder = ORFFinder(minimum_length=6)
    >>> orfs = finder.find("ATGGCAGGTGACCCGTGA")
    >>> orfs[0].protein_sequence
    'MAGDP'
    """

    def __init__(self, minimum_length: int = 30) -> None:
        if minimum_length < 6:
            raise ValueError("minimum_length must be ≥ 6")
        self.minimum_length = minimum_length

    def find(self, sequence: str) -> list[ORF]:
        """Find ORFs in all six reading frames of ``sequence``."""
        orfs: list[ORF] = []
        orfs.extend(self._scan_strand(sequence, "+"))
        rc = DNA(sequence).reverse_complement().sequence
        orfs.extend(self._scan_strand(rc, "-"))
        orfs.sort(key=lambda o: (o.start, o.strand))
        return orfs

    def iter_find(self, sequence: str) -> Iterator[ORF]:
        """Iterate over ORFs lazily."""
        yield from self.find(sequence)

    def _scan_strand(self, seq: str, strand: str) -> list[ORF]:
        seq = seq.upper()
        orfs: list[ORF] = []
        for frame in range(3):
            i = frame
            while i <= len(seq) - 3:
                codon = seq[i : i + 3]
                if codon == START_CODON:
                    start = i
                    protein: list[str] = []
                    j = i
                    stop_found = False
                    while j <= len(seq) - 3:
                        c = seq[j : j + 3]
                        if c in STOP_CODONS:
                            stop_found = True
                            break
                        aa = STANDARD_GENETIC_CODE.get(c, "X")
                        protein.append(aa)
                        j += 3
                    if stop_found:
                        end = j + 3
                        nuc = seq[start:end]
                        if len(nuc) >= self.minimum_length:
                            orfs.append(
                                ORF(
                                    start=start,
                                    end=end,
                                    frame=frame + 1,
                                    strand=strand,
                                    nucleotide_sequence=nuc,
                                    protein_sequence="".join(protein),
                                )
                            )
                        i = end
                        continue
                i += 3
        return orfs


__all__ = ["ORFFinder"]

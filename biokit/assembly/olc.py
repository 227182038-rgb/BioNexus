"""Greedy overlap-layout-consensus assembler."""

from __future__ import annotations

from collections.abc import Iterable

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from biokit.assembly.result import AssemblyResult
from biokit.exceptions import AssemblyError
from biokit.sequence.validation import validate_dna


class OverlapAssembler:
    """Greedy overlap-layout-consensus assembler.

    Parameters
    ----------
    min_overlap : int, optional
        Minimum overlap required to merge two reads (default 10).

    Examples
    --------
    >>> reads = ["ATGGCAGGTGAC", "CAGGTGACCCGTTGA"]
    >>> asm = OverlapAssembler(min_overlap=8)
    >>> result = asm.assemble(reads)
    >>> str(result.contigs[0].seq)
    'ATGGCAGGTGACCCGTTGA'
    """

    def __init__(self, min_overlap: int = 10) -> None:
        if min_overlap < 1:
            raise AssemblyError("min_overlap must be ≥ 1")
        self.min_overlap = min_overlap

    @staticmethod
    def _overlap(a: str, b: str, min_overlap: int) -> int:
        max_overlap = min(len(a), len(b))
        for k in range(max_overlap, min_overlap - 1, -1):
            if a.endswith(b[:k]):
                return k
        return 0

    def assemble(self, reads: Iterable[str]) -> AssemblyResult:
        """Assemble reads using greedy OLC."""
        seqs = []
        for read in reads:
            validate_dna(read)
            seqs.append(read.upper())
        if not seqs:
            return AssemblyResult(contigs=[], method="olc")
        contigs = list(seqs)
        changed = True
        while changed and len(contigs) > 1:
            changed = False
            best_i = best_j = -1
            best_overlap = self.min_overlap - 1
            best_merged: str | None = None
            for i in range(len(contigs)):
                for j in range(len(contigs)):
                    if i == j:
                        continue
                    ov = self._overlap(contigs[i], contigs[j], self.min_overlap)
                    if ov > best_overlap:
                        best_overlap = ov
                        best_i, best_j = i, j
                        best_merged = contigs[i] + contigs[j][ov:]
            if best_merged is not None:
                lo, hi = sorted([best_i, best_j])
                contigs.pop(hi)
                contigs.pop(lo)
                contigs.append(best_merged)
                changed = True
        records = [
            SeqRecord(Seq(c), id=f"contig_{i + 1}", description=f"length={len(c)}")
            for i, c in enumerate(contigs)
        ]
        return AssemblyResult(contigs=records, method="olc")


__all__ = ["OverlapAssembler"]

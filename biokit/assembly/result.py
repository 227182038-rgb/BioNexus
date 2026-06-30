"""Assembly result container."""

from __future__ import annotations

from dataclasses import dataclass, field

from Bio.SeqRecord import SeqRecord


@dataclass
class AssemblyResult:
    """Container for the output of an assembly."""

    contigs: list[SeqRecord] = field(default_factory=list)
    k: int = 0
    method: str = "debruijn"

    @property
    def total_length(self) -> int:
        """Sum of all contig lengths."""
        return sum(len(c.seq) for c in self.contigs)

    @property
    def longest_contig(self) -> int:
        """Length of the longest contig (0 if no contigs)."""
        return max((len(c.seq) for c in self.contigs), default=0)

    @property
    def num_contigs(self) -> int:
        """Number of contigs."""
        return len(self.contigs)


__all__ = ["AssemblyResult"]

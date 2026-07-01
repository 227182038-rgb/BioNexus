"""Assembly metrics: N50, L50, N90, GC content."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeAlias

from Bio.SeqRecord import SeqRecord

from biokit.statistics.sequence_stats import gc_fraction

ContigLike: TypeAlias = SeqRecord | int


def _lengths(contigs: Sequence[ContigLike]) -> list[int]:
    """Extract lengths from a mix of SeqRecord and int contigs, sorted desc."""
    out: list[int] = []
    for c in contigs:
        if isinstance(c, SeqRecord):
            out.append(len(str(c.seq)))
        else:
            out.append(int(c))
    return sorted(out, reverse=True)


def n50(contigs: Sequence[ContigLike]) -> int:
    """N50 statistic.

    Examples
    --------
    >>> n50([100, 200, 300, 400])
    300
    """
    lengths = _lengths(contigs)
    if not lengths:
        return 0
    total = sum(lengths)
    half = total / 2
    cumulative = 0
    for length in lengths:
        cumulative += length
        if cumulative >= half:
            return length
    return lengths[-1]


def l50(contigs: Sequence[ContigLike]) -> int:
    """L50 statistic (number of contigs whose summed length ≥ N50).

    Examples
    --------
    >>> l50([100, 200, 300, 400])
    2
    """
    lengths = _lengths(contigs)
    if not lengths:
        return 0
    total = sum(lengths)
    half = total / 2
    cumulative = 0
    for i, length in enumerate(lengths, start=1):
        cumulative += length
        if cumulative >= half:
            return i
    return len(lengths)


def n90(contigs: Sequence[ContigLike]) -> int:
    """N90 statistic."""
    lengths = _lengths(contigs)
    if not lengths:
        return 0
    total = sum(lengths)
    target = total * 0.9
    cumulative = 0
    for length in lengths:
        cumulative += length
        if cumulative >= target:
            return length
    return lengths[-1]


def assembly_gc(contigs: Sequence[SeqRecord]) -> float:
    """Weighted GC fraction across all contigs."""
    seq = "".join(str(c.seq) for c in contigs)
    return gc_fraction(seq)


__all__ = ["assembly_gc", "l50", "n50", "n90"]

"""Biopython SeqIO wrappers and shared sequence helpers."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from biokit.exceptions import InvalidFormatError
from biokit.sequence.dna import DNA
from biokit.statistics.sequence_stats import gc_fraction

PathLike = str | Path


def read_sequences(path: PathLike, fmt: str = "fasta") -> list[SeqRecord]:
    """Read all sequences from ``path`` in the requested format."""
    p = Path(path)
    if not p.exists():
        raise InvalidFormatError(f"file not found: {p}")
    try:
        # ``SeqIO.parse`` is untyped in the BioPython stubs; the runtime
        # contract is ``Iterator[SeqRecord]``.
        return list(SeqIO.parse(str(p), fmt))
    except Exception as exc:
        raise InvalidFormatError(f"could not parse {p} as {fmt}: {exc}") from exc


def write_sequences(records: Iterable[SeqRecord], path: PathLike, fmt: str = "fasta") -> int:
    """Write ``records`` to ``path`` in the requested format."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return SeqIO.write(records, str(p), fmt)


def iter_sequences(path: PathLike, fmt: str = "fasta") -> Iterator[SeqRecord]:
    """Iterate over records in ``path`` lazily."""
    p = Path(path)
    if not p.exists():
        raise InvalidFormatError(f"file not found: {p}")
    return SeqIO.parse(str(p), fmt)


def make_record(sequence: str, id: str, description: str = "") -> SeqRecord:
    """Create a :class:`SeqRecord` from a raw sequence string."""
    return SeqRecord(Seq(sequence), id=id, description=description)


def gc_content(sequence: str) -> float:
    """GC fraction in [0, 1]."""
    return gc_fraction(sequence)


def reverse_complement(sequence: str) -> str:
    """Reverse complement of a DNA sequence."""
    return DNA(sequence).reverse_complement().sequence


__all__ = [
    "gc_content",
    "iter_sequences",
    "make_record",
    "read_sequences",
    "reverse_complement",
    "write_sequences",
]

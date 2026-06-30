"""GenBank parser and writer (Biopython-backed)."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

from biokit.exceptions import InvalidFormatError


def parse_genbank(path: str | Path) -> list[SeqRecord]:
    """Parse a GenBank file into Biopython :class:`SeqRecord` objects.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to a GenBank file.

    Returns
    -------
    list[SeqRecord]
        All records in the file.
    """
    p = Path(path)
    if not p.exists():
        raise InvalidFormatError(f"file not found: {p}")
    try:
        return list(SeqIO.parse(str(p), "genbank"))
    except Exception as exc:
        raise InvalidFormatError(f"could not parse GenBank file {p}: {exc}") from exc


def write_genbank(records: Iterable[SeqRecord], path: str | Path) -> int:
    """Write records to a GenBank file.

    Returns
    -------
    int
        Number of records written.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return SeqIO.write(records, str(p), "genbank")


__all__ = ["parse_genbank", "write_genbank"]

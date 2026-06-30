"""FASTA parser and writer."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import NamedTuple

from biokit.constants import FASTA_EXTENSIONS, FASTA_LINE_WIDTH
from biokit.exceptions import InvalidFormatError


class FastaRecord(NamedTuple):
    """A single FASTA record."""

    id: str
    description: str
    sequence: str


def parse_fasta(path_or_text: str | Path) -> Iterator[FastaRecord]:
    """Parse FASTA from a file path or raw text.

    Parameters
    ----------
    path_or_text : str or pathlib.Path
        Path to a FASTA file, or raw FASTA text.

    Yields
    ------
    FastaRecord
        Each record in the file.

    Examples
    --------
    >>> records = list(parse_fasta(">seq1 desc\\nATGC\\n>seq2\\nGGCC"))
    >>> len(records)
    2
    >>> records[0].id
    'seq1'
    >>> records[0].sequence
    'ATGC'
    """
    text = _resolve_input(path_or_text)
    header: str = ""
    description: str = ""
    seq_lines: list[str] = []
    for line in text.splitlines():
        if not line:
            continue
        if line.startswith(">"):
            if header:
                yield FastaRecord(header, description, "".join(seq_lines))
            parts = line[1:].split(None, 1)
            header = parts[0] if parts else ""
            description = parts[1] if len(parts) > 1 else ""
            seq_lines = []
        else:
            seq_lines.append(line.strip())
    if header:
        yield FastaRecord(header, description, "".join(seq_lines))


def write_fasta(
    records: Iterable[FastaRecord], path: str | Path, line_width: int = FASTA_LINE_WIDTH
) -> int:
    """Write records to a FASTA file.

    Parameters
    ----------
    records : iterable of FastaRecord
        Records to write.
    path : str or pathlib.Path
        Output file path.
    line_width : int, optional
        Maximum line width for the sequence (default 70).

    Returns
    -------
    int
        Number of records written.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w") as fh:
        for record in records:
            header = f">{record.id}"
            if record.description:
                header += f" {record.description}"
            fh.write(header + "\n")
            seq = record.sequence
            for i in range(0, len(seq), line_width):
                fh.write(seq[i : i + line_width] + "\n")
            count += 1
    return count


def _resolve_input(path_or_text: str | Path) -> str:
    """Return the contents of a file path or pass-through the text."""
    s = str(path_or_text)
    if s.startswith(">"):
        return s  # Looks like FASTA text
    p = Path(s)
    if p.exists():
        if p.suffix.lower() not in FASTA_EXTENSIONS:
            raise InvalidFormatError(
                f"unrecognised FASTA extension: {p.suffix!r}. "
                f"Expected one of: {sorted(FASTA_EXTENSIONS)}"
            )
        return p.read_text()
    raise InvalidFormatError(f"file not found: {p}")


__all__ = ["FastaRecord", "parse_fasta", "write_fasta"]

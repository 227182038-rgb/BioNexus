"""FASTQ parser."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

from biokit.exceptions import InvalidFormatError


class FastqRecord(NamedTuple):
    """A single FASTQ record."""

    id: str
    description: str
    sequence: str
    quality: str

    @property
    def average_quality(self) -> float:
        """Average Phred quality score."""
        if not self.quality:
            return 0.0
        return sum(ord(c) - 33 for c in self.quality) / len(self.quality)


def parse_fastq(path_or_text: str | Path) -> Iterator[FastqRecord]:
    """Parse FASTQ from a file path or raw text.

    Parameters
    ----------
    path_or_text : str or pathlib.Path
        Path to a FASTQ file, or raw FASTQ text.

    Yields
    ------
    FastqRecord
        Each record in the file.
    """
    text = _resolve_input(path_or_text)
    lines = [line.rstrip("\n") for line in text.splitlines() if line]
    if len(lines) % 4 != 0:
        raise InvalidFormatError("FASTQ must have a multiple of 4 lines")
    for i in range(0, len(lines), 4):
        header_line = lines[i]
        if not header_line.startswith("@"):
            raise InvalidFormatError(f"expected '@' header at line {i + 1}")
        parts = header_line[1:].split(None, 1)
        seq_id = parts[0] if parts else ""
        description = parts[1] if len(parts) > 1 else ""
        seq = lines[i + 1]
        plus = lines[i + 2]
        qual = lines[i + 3]
        if not plus.startswith("+"):
            raise InvalidFormatError(f"expected '+' separator at line {i + 3}")
        if len(seq) != len(qual):
            raise InvalidFormatError(
                f"sequence and quality lengths differ at record starting line {i + 1}"
            )
        yield FastqRecord(seq_id, description, seq, qual)


def _resolve_input(path_or_text: str | Path) -> str:
    s = str(path_or_text)
    if s.startswith("@"):
        return s
    p = Path(s)
    if p.exists():
        return p.read_text()
    raise InvalidFormatError(f"file not found: {p}")


__all__ = ["FastqRecord", "parse_fastq"]

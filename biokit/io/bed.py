"""BED parser and writer."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from biokit.exceptions import InvalidFormatError


@dataclass(slots=True)
class BEDFeature:
    """A single BED interval.

    Coordinates follow BED convention: 0-based, half-open.
    """

    chrom: str
    start: int
    end: int
    name: str = "."
    score: str = "."
    strand: str = "."

    @property
    def length(self) -> int:
        """Interval length in nucleotides."""
        return self.end - self.start


def parse_bed(path_or_text: str | Path) -> Iterator[BEDFeature]:
    """Parse BED from a file path or raw text.

    Yields
    ------
    BEDFeature
        Each BED interval.
    """
    text = _resolve_input(path_or_text)
    for lineno, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if (
            not line
            or line.startswith("#")
            or line.startswith("track")
            or line.startswith("browser")
        ):
            continue
        fields = line.split("\t")
        if len(fields) < 3:
            raise InvalidFormatError(f"line {lineno}: expected ≥3 columns, got {len(fields)}")
        yield BEDFeature(
            chrom=fields[0],
            start=int(fields[1]),
            end=int(fields[2]),
            name=fields[3] if len(fields) > 3 else ".",
            score=fields[4] if len(fields) > 4 else ".",
            strand=fields[5] if len(fields) > 5 else ".",
        )


def write_bed(features: Iterable[BEDFeature], path: str | Path) -> int:
    """Write features to a BED file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w") as fh:
        for feat in features:
            fh.write(
                f"{feat.chrom}\t{feat.start}\t{feat.end}\t{feat.name}\t{feat.score}\t{feat.strand}\n"
            )
            count += 1
    return count


def _resolve_input(path_or_text: str | Path) -> str:
    s = str(path_or_text)
    p = Path(s)
    if p.exists():
        return p.read_text()
    if "\t" in s:
        return s
    raise InvalidFormatError(f"file not found: {p}")


__all__ = ["BEDFeature", "parse_bed", "write_bed"]

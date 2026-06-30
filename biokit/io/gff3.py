"""GFF3 parser and writer."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from biokit.exceptions import InvalidFormatError


@dataclass(slots=True)
class GFF3Feature:
    """A single GFF3 feature."""

    seqid: str
    source: str
    type: str
    start: int
    end: int
    score: str
    strand: str
    phase: str
    attributes: dict[str, str] = field(default_factory=dict)

    @property
    def length(self) -> int:
        """Feature length in nucleotides."""
        return self.end - self.start + 1


def parse_gff3(path_or_text: str | Path) -> Iterator[GFF3Feature]:
    """Parse GFF3 from a file path or raw text.

    Parameters
    ----------
    path_or_text : str or pathlib.Path
        Path to a GFF3 file, or raw GFF3 text.

    Yields
    ------
    GFF3Feature
        Each feature in the file.

    Examples
    --------
    >>> feats = list(
    ...     parse_gff3("##gff-version 3\\nchr1\\tsrc\\tgene\\t1\\t100\\t.\\t+\\t.\\tID=g1")
    ... )
    >>> feats[0].type
    'gene'
    >>> feats[0].attributes["ID"]
    'g1'
    """
    text = _resolve_input(path_or_text)
    for lineno, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) < 8:
            raise InvalidFormatError(f"line {lineno}: expected ≥8 columns, got {len(fields)}")
        seqid, source, ftype, start, end, score, strand, phase = fields[:8]
        attrs: dict[str, str] = {}
        if len(fields) > 8 and fields[8] != ".":
            for kv in fields[8].split(";"):
                kv = kv.strip()
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    attrs[k.strip()] = v.strip()
        yield GFF3Feature(
            seqid=seqid,
            source=source,
            type=ftype,
            start=int(start),
            end=int(end),
            score=score,
            strand=strand,
            phase=phase,
            attributes=attrs,
        )


def write_gff3(features: Iterable[GFF3Feature], path: str | Path) -> int:
    """Write features to a GFF3 file.

    Returns
    -------
    int
        Number of features written.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w") as fh:
        fh.write("##gff-version 3\n")
        for feat in features:
            attrs = ";".join(f"{k}={v}" for k, v in feat.attributes.items())
            fh.write(
                f"{feat.seqid}\t{feat.source}\t{feat.type}\t{feat.start}\t{feat.end}\t"
                f"{feat.score}\t{feat.strand}\t{feat.phase}\t{attrs}\n"
            )
            count += 1
    return count


def _resolve_input(path_or_text: str | Path) -> str:
    s = str(path_or_text)
    if s.startswith("##gff-version") or "\t" in s:
        return s
    p = Path(s)
    if p.exists():
        return p.read_text()
    raise InvalidFormatError(f"file not found: {p}")


__all__ = ["GFF3Feature", "parse_gff3", "write_gff3"]

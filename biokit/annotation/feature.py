"""Annotation feature dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Bio.SeqFeature import SeqFeature


@dataclass
class AnnotationFeature:
    """A format-agnostic genomic feature."""

    seqid: str
    source: str = "."
    type: str = "feature"
    start: int = 1
    end: int = 1
    strand: str = "+"
    phase: int = -1
    attributes: dict[str, str] = field(default_factory=dict)

    @property
    def length(self) -> int:
        """Feature length in nucleotides."""
        return self.end - self.start + 1

    def to_seq_feature(self) -> SeqFeature:
        """Convert to a Biopython :class:`SeqFeature`."""
        from Bio.SeqFeature import SeqFeature, SimpleLocation

        strand_value = 1 if self.strand == "+" else -1 if self.strand == "-" else 0
        location = SimpleLocation(self.start - 1, self.end, strand=strand_value)
        qualifiers = {k: [v] for k, v in self.attributes.items()}
        qualifiers.setdefault("source", [self.source])
        return SeqFeature(location=location, type=self.type, qualifiers=qualifiers)


__all__ = ["AnnotationFeature"]

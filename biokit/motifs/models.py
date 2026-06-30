"""Motif data model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Motif:
    """A sequence motif."""

    sequence: str
    positions: list[int] = field(default_factory=list)

    @property
    def length(self) -> int:
        """Motif length."""
        return len(self.sequence)

    @property
    def count(self) -> int:
        """Number of occurrences."""
        return len(self.positions)


__all__ = ["Motif"]

"""Restriction site mapper."""

from __future__ import annotations

from biokit.restriction.enzyme import Enzyme


def cut_site(enzyme: Enzyme, sequence: str) -> list[int]:
    """Return all 0-based cut positions of ``enzyme`` in ``sequence``.

    Examples
    --------
    >>> from biokit.restriction import Enzyme
    >>> e = Enzyme("EcoRI", "GAATTC", 1)
    >>> cut_site(e, "GAATTCAAAGAATTC")
    [1, 10]
    """
    seq = sequence.upper()
    site = enzyme.recognition_site.upper()
    positions: list[int] = []
    start = 0
    while True:
        idx = seq.find(site, start)
        if idx < 0:
            break
        positions.append(idx + enzyme.cut_position)
        start = idx + 1
    return positions


class RestrictionMapper:
    """Map restriction enzymes to their cut sites in a sequence."""

    def map(self, enzyme: Enzyme, sequence: str) -> list[int]:
        """Return all cut positions for ``enzyme`` in ``sequence``."""
        return cut_site(enzyme, sequence)


__all__ = ["RestrictionMapper", "cut_site"]

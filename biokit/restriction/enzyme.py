"""Restriction enzyme data model and database."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Enzyme:
    """A restriction enzyme.

    Attributes
    ----------
    name : str
        Enzyme name (e.g. ``"EcoRI"``).
    recognition_site : str
        Recognition sequence (e.g. ``"GAATTC"``).
    cut_position : int
        Cut position relative to the start of the recognition site (0-based).
    """

    name: str
    recognition_site: str
    cut_position: int


class RestrictionEnzymeDatabase:
    """A small built-in database of common restriction enzymes."""

    ENZYMES: dict[str, Enzyme] = {
        "EcoRI": Enzyme("EcoRI", "GAATTC", 1),
        "BamHI": Enzyme("BamHI", "GGATCC", 1),
        "HindIII": Enzyme("HindIII", "AAGCTT", 1),
        "XhoI": Enzyme("XhoI", "CTCGAG", 1),
        "NotI": Enzyme("NotI", "GCGGCCGC", 2),
        "EcoRV": Enzyme("EcoRV", "GATATC", 3),
        "SmaI": Enzyme("SmaI", "CCCGGG", 3),
        "KpnI": Enzyme("KpnI", "GGTACC", 5),
        "PstI": Enzyme("PstI", "CTGCAG", 5),
        "SalI": Enzyme("SalI", "GTCGAC", 1),
    }

    def get(self, name: str) -> Enzyme:
        """Look up an enzyme by name (case-insensitive)."""
        # Try exact match first, then case-insensitive lookup
        if name in self.ENZYMES:
            return self.ENZYMES[name]
        name_lower = name.lower()
        for key, enzyme in self.ENZYMES.items():
            if key.lower() == name_lower:
                return enzyme
        raise KeyError(f"unknown enzyme: {name!r}")

    def all(self) -> list[Enzyme]:
        """Return all enzymes in the database."""
        return list(self.ENZYMES.values())


__all__ = ["Enzyme", "RestrictionEnzymeDatabase"]

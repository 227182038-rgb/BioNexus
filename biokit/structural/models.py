"""Structural data models."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AtomInfo:
    """Compact representation of a single atom."""

    chain_id: str
    residue_id: str
    residue_name: str
    atom_name: str
    element: str
    coord: np.ndarray


@dataclass
class StructureStats:
    """Summary statistics for a 3-D structure."""

    num_chains: int = 0
    num_residues: int = 0
    num_atoms: int = 0
    helix_fraction: float = 0.0
    sheet_fraction: float = 0.0
    coil_fraction: float = 0.0


__all__ = ["AtomInfo", "StructureStats"]

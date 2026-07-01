"""Distance matrix and RMSD calculations."""

from __future__ import annotations

import numpy as np
from Bio.PDB.Structure import Structure
from numpy.typing import NDArray

from biokit.exceptions import StructuralError
from biokit.structural.loader import iter_atoms


def distance_matrix(structure: Structure, atom_filter: str | None = "CA") -> NDArray[np.float64]:
    """Pairwise distance matrix for atoms in ``structure``."""
    atoms = list(iter_atoms(structure))
    if atom_filter is not None:
        atoms = [a for a in atoms if a.atom_name == atom_filter]
    if not atoms:
        return np.zeros((0, 0), dtype=np.float64)
    coords: NDArray[np.float64] = np.array([a.coord for a in atoms], dtype=np.float64)
    diff = coords[:, None, :] - coords[None, :, :]
    result: NDArray[np.float64] = np.sqrt((diff * diff).sum(axis=-1))
    return result


def rmsd(structure_a: Structure, structure_b: Structure, atom_filter: str = "CA") -> float:
    """RMSD between two structures (filtered atoms must match in count)."""
    a = [a for a in iter_atoms(structure_a) if a.atom_name == atom_filter]
    b = [a for a in iter_atoms(structure_b) if a.atom_name == atom_filter]
    if len(a) != len(b):
        raise StructuralError(f"atom count mismatch: {len(a)} vs {len(b)} for {atom_filter!r}")
    if not a:
        return 0.0
    ac: NDArray[np.float64] = np.array([x.coord for x in a], dtype=np.float64)
    bc: NDArray[np.float64] = np.array([x.coord for x in b], dtype=np.float64)
    diff = ac - bc
    return float(np.sqrt((diff * diff).sum() / len(a)))


def kabsch_rmsd(
    structure_a: Structure,
    structure_b: Structure,
    atom_filter: str = "CA",
) -> float:
    """RMSD after optimal Kabsch superposition."""
    a = [a for a in iter_atoms(structure_a) if a.atom_name == atom_filter]
    b = [a for a in iter_atoms(structure_b) if a.atom_name == atom_filter]
    if len(a) != len(b):
        raise StructuralError(f"atom count mismatch: {len(a)} vs {len(b)} for {atom_filter!r}")
    if not a:
        return 0.0
    ac: NDArray[np.float64] = np.array([x.coord for x in a], dtype=np.float64)
    bc: NDArray[np.float64] = np.array([x.coord for x in b], dtype=np.float64)
    a_centroid = ac.mean(axis=0)
    b_centroid = bc.mean(axis=0)
    a2 = ac - a_centroid
    b2 = bc - b_centroid
    h = a2.T @ b2
    u, _, vh = np.linalg.svd(h)
    d = np.linalg.det(vh.T @ u.T)
    sign = np.diag([1.0, 1.0, np.sign(d)])
    rotation = vh.T @ sign @ u.T
    a_aligned = a2 @ rotation.T
    diff = a_aligned - b2
    return float(np.sqrt((diff * diff).sum() / len(a)))


__all__ = ["distance_matrix", "kabsch_rmsd", "rmsd"]

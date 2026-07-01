"""PDB loading and atom iteration."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import numpy as np
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB.Structure import Structure

from biokit.exceptions import StructuralError
from biokit.structural.models import AtomInfo

PathLike = str | Path


def load_structure(
    path: PathLike,
    name: str | None = None,
    parser: PDBParser | None = None,
) -> Structure:
    """Load a PDB file into a Biopython :class:`Structure`.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the PDB file.
    name : str, optional
        Structure name (defaults to the file stem).
    parser : Bio.PDB.PDBParser.PDBParser, optional
        Custom parser. A default :class:`PDBParser` is used otherwise.

    Returns
    -------
    Bio.PDB.Structure.Structure
        The parsed structure.

    Raises
    ------
    StructuralError
        If the file does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise StructuralError(f"file not found: {p}")
    name = name or p.stem
    if parser is None:
        parser = PDBParser(QUIET=True)
    structure: Structure = parser.get_structure(name, str(p))
    return structure


def iter_atoms(structure: Structure) -> Iterator[AtomInfo]:
    """Yield :class:`AtomInfo` for every non-hetero atom in ``structure``."""
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.id[0].strip():  # skip hetero/water
                    continue
                for atom in residue:
                    yield AtomInfo(
                        chain_id=chain.id,
                        residue_id=str(residue.id[1]),
                        residue_name=residue.get_resname(),
                        atom_name=atom.get_name(),
                        element=atom.element or "",
                        coord=np.asarray(atom.coord, dtype=float),
                    )


def backbone_atoms(structure: Structure) -> list[AtomInfo]:
    """Return backbone atoms (N, CA, C, O)."""
    return [a for a in iter_atoms(structure) if a.atom_name in {"N", "CA", "C", "O"}]


__all__ = ["backbone_atoms", "iter_atoms", "load_structure"]

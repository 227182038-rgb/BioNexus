"""Structure statistics summary."""

from __future__ import annotations

from Bio.PDB.Structure import Structure

from biokit.structural.loader import iter_atoms
from biokit.structural.models import StructureStats
from biokit.structural.secondary import secondary_structure_fractions


def structure_stats(structure: Structure) -> StructureStats:
    """Compute summary statistics for a structure."""
    atoms = list(iter_atoms(structure))
    residues = {(a.chain_id, a.residue_id, a.residue_name) for a in atoms}
    chains = {a.chain_id for a in atoms}
    h, s, c = secondary_structure_fractions(structure)
    return StructureStats(
        num_chains=len(chains),
        num_residues=len(residues),
        num_atoms=len(atoms),
        helix_fraction=h,
        sheet_fraction=s,
        coil_fraction=c,
    )


__all__ = ["structure_stats"]

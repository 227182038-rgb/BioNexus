"""Secondary-structure estimation."""

from __future__ import annotations

from Bio.PDB.Polypeptide import PPBuilder
from Bio.PDB.Structure import Structure


def secondary_structure_fractions(structure: Structure) -> tuple[float, float, float]:
    """Estimate helix/sheet/coil fractions from backbone dihedrals.

    Returns
    -------
    tuple[float, float, float]
        ``(helix_fraction, sheet_fraction, coil_fraction)``.
    """
    ppb = PPBuilder()
    helix = sheet = coil = 0
    total = 0
    for pp in ppb.build_peptides(structure):
        for entry in pp.get_phi_psi_list():
            phi, psi = entry
            if phi is None or psi is None:
                continue
            total += 1
            if -90 < phi < -30 and -60 < psi < 30:
                helix += 1
            elif -150 < phi < -60 and 90 < psi < 180:
                sheet += 1
            else:
                coil += 1
    if total == 0:
        return 0.0, 0.0, 0.0
    return helix / total, sheet / total, coil / total


__all__ = ["secondary_structure_fractions"]

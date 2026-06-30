"""Tests for biokit.structural."""

from __future__ import annotations

import numpy as np
import pytest
from biokit.exceptions import StructuralError
from biokit.structural import (
    AtomInfo,
    StructureStats,
    backbone_atoms,
    distance_matrix,
    iter_atoms,
    kabsch_rmsd,
    load_structure,
    rmsd,
    structure_stats,
)


def test_load_structure_basic():
    structure = load_structure("tests/data/sample.pdb")
    assert structure.id == "sample"


def test_load_structure_missing_file():
    with pytest.raises(StructuralError):
        load_structure("tests/data/missing.pdb")


def test_iter_atoms_yields_atom_info():
    structure = load_structure("tests/data/sample.pdb")
    atoms = list(iter_atoms(structure))
    assert len(atoms) > 0
    assert all(isinstance(a, AtomInfo) for a in atoms)
    assert all(a.coord.shape == (3,) for a in atoms)


def test_backbone_atoms_filter():
    structure = load_structure("tests/data/sample.pdb")
    bb = backbone_atoms(structure)
    assert all(a.atom_name in {"N", "CA", "C", "O"} for a in bb)


def test_distance_matrix_symmetric():
    structure = load_structure("tests/data/sample.pdb")
    mat = distance_matrix(structure, atom_filter="CA")
    assert mat.shape[0] == mat.shape[1]
    assert np.allclose(mat, mat.T)
    assert np.allclose(np.diag(mat), 0.0)


def test_rmsd_self_is_zero():
    structure = load_structure("tests/data/sample.pdb")
    assert rmsd(structure, structure, atom_filter="CA") == pytest.approx(0.0)


def test_kabsch_rmsd_self_is_zero():
    structure = load_structure("tests/data/sample.pdb")
    assert kabsch_rmsd(structure, structure, atom_filter="CA") == pytest.approx(0.0, abs=1e-6)


def test_structure_stats():
    structure = load_structure("tests/data/sample.pdb")
    stats = structure_stats(structure)
    assert isinstance(stats, StructureStats)
    assert stats.num_atoms > 0

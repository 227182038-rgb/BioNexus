"""Tests for biokit.structural.

All file paths use the absolute ``sample_pdb_path`` fixture from
``conftest.py`` so the tests are working-directory-independent.
"""

from __future__ import annotations

from pathlib import Path

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


def test_load_structure_basic(sample_pdb_path: Path):
    structure = load_structure(sample_pdb_path)
    assert structure.id == "sample"


def test_load_structure_missing_file():
    with pytest.raises(StructuralError):
        load_structure("nonexistent_file.pdb")


def test_iter_atoms_yields_atom_info(sample_pdb_path: Path):
    structure = load_structure(sample_pdb_path)
    atoms = list(iter_atoms(structure))
    assert len(atoms) > 0
    assert all(isinstance(a, AtomInfo) for a in atoms)
    assert all(a.coord.shape == (3,) for a in atoms)


def test_backbone_atoms_filter(sample_pdb_path: Path):
    structure = load_structure(sample_pdb_path)
    bb = backbone_atoms(structure)
    assert all(a.atom_name in {"N", "CA", "C", "O"} for a in bb)


def test_distance_matrix_symmetric(sample_pdb_path: Path):
    structure = load_structure(sample_pdb_path)
    mat = distance_matrix(structure, atom_filter="CA")
    assert mat.shape[0] == mat.shape[1]
    assert np.allclose(mat, mat.T)
    assert np.allclose(np.diag(mat), 0.0)


def test_rmsd_self_is_zero(sample_pdb_path: Path):
    structure = load_structure(sample_pdb_path)
    assert rmsd(structure, structure, atom_filter="CA") == pytest.approx(0.0)


def test_kabsch_rmsd_self_is_zero(sample_pdb_path: Path):
    structure = load_structure(sample_pdb_path)
    assert kabsch_rmsd(structure, structure, atom_filter="CA") == pytest.approx(0.0, abs=1e-6)


def test_structure_stats(sample_pdb_path: Path):
    structure = load_structure(sample_pdb_path)
    stats = structure_stats(structure)
    assert isinstance(stats, StructureStats)
    assert stats.num_atoms > 0

"""Shared pytest fixtures.

The ``chdir_to_project_root`` fixture (autouse) changes the working directory
to the project root before every test, so tests that use relative paths like
``"tests/data/sample.pdb"`` resolve correctly regardless of where pytest is
invoked from. This makes the whole suite working-directory-independent.
"""

from __future__ import annotations

from pathlib import Path

import pytest

#: Absolute path to the project root (the folder containing ``pyproject.toml``).
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def chdir_to_project_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """``cd`` to the project root before every test.

    Uses ``monkeypatch`` so the original working directory is restored
    automatically after the test, even if the test changes it again.
    """
    monkeypatch.chdir(PROJECT_ROOT)


@pytest.fixture
def sample_dna() -> str:
    """A short DNA sequence with an ORF."""
    return "ATGGCAGGTGACCCGTGA"


@pytest.fixture
def sample_rna() -> str:
    """A short RNA sequence."""
    return "AUGGCAGGUGACCCGUGA"


@pytest.fixture
def sample_protein() -> str:
    """A short protein sequence."""
    return "MAGDPV"


@pytest.fixture
def test_data_dir() -> Path:
    """Absolute path to the test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_pdb_path(test_data_dir: Path) -> Path:
    """Absolute path to ``tests/data/sample.pdb``."""
    return test_data_dir / "sample.pdb"


@pytest.fixture
def sample_fasta_text() -> str:
    """Inline FASTA text."""
    return ">seq1 description here\nATGGCAGGTGAC\nCCGTGA\n>seq2\nGGTGACCCGTTGA\n"

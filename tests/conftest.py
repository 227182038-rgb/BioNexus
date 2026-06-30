"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


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
    """Path to the test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_fasta_text() -> str:
    """Inline FASTA text."""
    return ">seq1 description here\nATGGCAGGTGAC\nCCGTGA\n>seq2\nGGTGACCCGTTGA\n"

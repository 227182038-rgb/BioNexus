"""Tests for biokit.orf."""

from __future__ import annotations

from biokit.orf import ORFFinder


def test_find_orfs_basic():
    finder = ORFFinder(minimum_length=6)
    orfs = finder.find("ATGGCAGGTGACCCGTGA")
    assert len(orfs) >= 1
    assert orfs[0].protein_sequence == "MAGDP"
    assert orfs[0].frame == 1
    assert orfs[0].strand == "+"


def test_no_orfs():
    finder = ORFFinder(minimum_length=6)
    orfs = finder.find("GCGCGCGCGCGC")
    assert orfs == []


def test_minimum_length_filter():
    finder = ORFFinder(minimum_length=100)
    orfs = finder.find("ATGGCAGGTGACCCGTGA")
    assert orfs == []

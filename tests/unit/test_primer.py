"""Tests for biokit.primer."""

from __future__ import annotations

import pytest
from biokit.exceptions import InvalidSequenceError, PrimerError
from biokit.primer import (
    DEFAULT_TM_TARGET,
    PrimerCandidate,
    design_primer,
    gc_clamp_score,
    has_hairpin,
    max_self_complementarity,
    score_primer,
    tm_gc,
    tm_nearest_neighbor,
    tm_wallace,
)


def test_tm_wallace():
    assert tm_wallace("ATGCATGC") == 24.0


def test_tm_gc_basic():
    assert 30 < tm_gc("ATGCATGCATGCATGCATGC") < 80
    assert tm_gc("") == 0.0


def test_tm_nearest_neighbor_short():
    with pytest.raises(PrimerError):
        tm_nearest_neighbor("A")


def test_gc_clamp_score():
    assert gc_clamp_score("ATGCAAAAAA") == 0
    assert gc_clamp_score("ATGCATGCGG") == 4  # last 5 = TGCGG


def test_max_self_complementarity_palindrome():
    assert max_self_complementarity("ATCGAT") >= 6
    assert max_self_complementarity("AAAAA") == 0


def test_has_hairpin():
    assert has_hairpin("ATCGAT", min_stem=4)
    assert not has_hairpin("AAAAAA", min_stem=4)


def test_design_primer_returns_candidates():
    primers = design_primer("ATGGCAGGTGACCCGTTGACCGTACGTAACGCATGCAGT", length=20)
    assert len(primers) > 0
    for p in primers:
        assert isinstance(p, PrimerCandidate)
        assert len(p.sequence) == 20


def test_design_primer_invalid_sequence():
    with pytest.raises(InvalidSequenceError):
        design_primer("ATGCXYZ", length=4)


def test_design_primer_invalid_length():
    with pytest.raises(PrimerError):
        design_primer("ATGC", length=4)


def test_score_primer_ideal_beats_bad():
    good = PrimerCandidate(
        sequence="ATGCATGCATGCATGCATGC",
        start=1,
        end=20,
        strand="+",
        tm=60.0,
        gc=0.5,
        self_comp=2,
        gc_clamp=2,
    )
    bad = PrimerCandidate(
        sequence="AAAAATTTTTAAAATTTTTT",
        start=1,
        end=20,
        strand="+",
        tm=30.0,
        gc=0.0,
        self_comp=8,
        gc_clamp=0,
    )
    assert score_primer(good) > score_primer(bad)


def test_default_tm_target():
    assert DEFAULT_TM_TARGET == 60.0

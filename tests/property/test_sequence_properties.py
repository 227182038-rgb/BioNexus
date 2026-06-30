"""Property-based tests using Hypothesis."""

from __future__ import annotations

import pytest

try:
    from hypothesis import given
    from hypothesis import strategies as st
except ImportError:  # pragma: no cover
    pytest.skip("hypothesis not installed", allow_module_level=True)

from biokit.sequence import DNA
from biokit.statistics.sequence_stats import gc_fraction


@given(st.text(alphabet="ACGT", min_size=1, max_size=200))
def test_gc_fraction_in_range(seq):
    """GC fraction must always be in [0, 1]."""
    assert 0.0 <= gc_fraction(seq) <= 1.0


@given(st.text(alphabet="ACGT", min_size=1, max_size=200))
def test_dna_round_trip_complement(seq):
    """complement(complement(seq)) == seq."""
    dna = DNA(seq)
    assert dna.complement().complement().sequence == dna.sequence


@given(st.text(alphabet="ACGT", min_size=1, max_size=200))
def test_reverse_complement_idempotent(seq):
    """reverse_complement(reverse_complement(seq)) == seq."""
    dna = DNA(seq)
    assert dna.reverse_complement().reverse_complement().sequence == dna.sequence


@given(st.text(alphabet="ACGT", min_size=3, max_size=300))
def test_dna_length_preserved(seq):
    """All DNA operations should preserve length."""
    dna = DNA(seq)
    assert len(dna.complement()) == len(dna)
    assert len(dna.reverse_complement()) == len(dna)


@given(st.text(alphabet="ACGT", min_size=3, max_size=300))
def test_gc_plus_at_equals_one(seq):
    """GC + AT fractions sum to 1 for ACGT-only sequences."""
    seq_u = seq.upper()
    gc = gc_fraction(seq_u)
    at = (seq_u.count("A") + seq_u.count("T")) / len(seq_u)
    assert abs((gc + at) - 1.0) < 1e-9

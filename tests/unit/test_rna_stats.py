"""Tests for biokit.rna and biokit.statistics."""

from __future__ import annotations

import pytest
from biokit.exceptions import InvalidSequenceError
from biokit.rna import complement, gc_rna, reverse_transcribe, transcribe
from biokit.statistics import gc_fraction, nucleotide_counts, sequence_complexity


class TestRNA:
    """RNA operations tests."""

    def test_transcribe(self):
        assert transcribe("ATGC") == "AUGC"

    def test_transcribe_invalid(self):
        with pytest.raises(InvalidSequenceError):
            transcribe("AUGC")

    def test_reverse_transcribe(self):
        assert reverse_transcribe("AUGC") == "ATGC"

    def test_complement_dna(self):
        assert complement("ATGC") == "TACG"

    def test_complement_rna(self):
        assert complement("AUGC") == "UACG"

    def test_gc_rna(self):
        assert gc_rna("AUGGCA") == 0.5


class TestStatistics:
    """Statistics tests."""

    def test_gc_fraction(self):
        assert gc_fraction("ATGC") == 0.5
        assert gc_fraction("GGCC") == 1.0
        assert gc_fraction("ATAT") == 0.0
        assert gc_fraction("") == 0.0

    def test_nucleotide_counts(self):
        assert nucleotide_counts("AATGC") == {"A": 2, "T": 1, "G": 1, "C": 1}

    def test_sequence_complexity_low(self):
        assert sequence_complexity("AAAAAA") == 0.0

    def test_sequence_complexity_high(self):
        assert sequence_complexity("ACGT") > 1.9

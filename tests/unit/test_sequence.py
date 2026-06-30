"""Tests for biokit.sequence."""

from __future__ import annotations

import pytest
from biokit.exceptions import InvalidSequenceError
from biokit.sequence import DNA, RNA, Protein, is_dna, is_rna, validate_dna


class TestDNA:
    """DNA value type tests."""

    def test_construction(self):
        dna = DNA("ATGGCAGGT")
        assert dna.length == 9
        assert dna.sequence == "ATGGCAGGT"

    def test_uppercased(self):
        assert DNA("atgc").sequence == "ATGC"

    def test_empty_raises(self):
        with pytest.raises(InvalidSequenceError):
            DNA("")

    def test_invalid_chars_raise(self):
        with pytest.raises(InvalidSequenceError):
            DNA("ATGCXYZ")

    def test_gc_content(self):
        assert DNA("ATGC").gc_content == 0.5
        assert DNA("GGCC").gc_content == 1.0
        assert DNA("ATAT").gc_content == 0.0

    def test_complement(self):
        assert DNA("ATGC").complement().sequence == "TACG"

    def test_reverse_complement(self):
        assert DNA("ATGC").reverse_complement().sequence == "GCAT"

    def test_transcribe(self):
        assert DNA("ATGGCAGGTGACCCGTGA").transcribe().sequence == "AUGGCAGGUGACCCGUGA"

    def test_translate(self):
        assert DNA("ATGGCAGGTGACCCGTGA").translate().sequence == "MAGDP"

    def test_eq_and_hash(self):
        a = DNA("ATGC")
        b = DNA("ATGC")
        c = DNA("GGCC")
        assert a == b
        assert a != c
        assert hash(a) == hash(b)
        assert hash(a) != hash(c)

    def test_indexing(self):
        dna = DNA("ATGCATGC")
        assert dna[0:3].sequence == "ATG"

    def test_iter(self):
        assert list(DNA("ATGC")) == ["A", "T", "G", "C"]


class TestRNA:
    """RNA value type tests."""

    def test_reverse_transcribe(self):
        assert RNA("AUGGCA").reverse_transcribe().sequence == "ATGGCA"

    def test_invalid_chars(self):
        with pytest.raises(InvalidSequenceError):
            RNA("AUGCXYZ")  # T is invalid for RNA


class TestProtein:
    """Protein value type tests."""

    def test_molecular_weight_positive(self):
        assert Protein("MAGDPV").molecular_weight > 0


class TestValidation:
    """Validation helper tests."""

    def test_is_dna(self):
        assert is_dna("ATGC")
        assert not is_dna("AUGC")
        assert not is_dna("ATGCX")

    def test_is_rna(self):
        assert is_rna("AUGC")
        assert not is_rna("ATGC")

    def test_validate_dna_passes(self):
        validate_dna("ATGCNRYSWKMBDHV-")  # IUPAC + gap

    def test_validate_dna_raises(self):
        with pytest.raises(InvalidSequenceError):
            validate_dna("ATGCX")

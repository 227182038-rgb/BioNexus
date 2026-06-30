"""Tests for biokit.translation and biokit.codon."""

from __future__ import annotations

import pytest
from biokit.codon import CodonUsage
from biokit.exceptions import InvalidSequenceError
from biokit.translation import Translator


class TestTranslator:
    """Translator tests."""

    def test_translate_basic(self):
        assert Translator().translate("ATGGCAGGTGACCCGTGA") == "MAGDP"

    def test_translate_rna(self):
        assert Translator().translate("AUGGCAGGUGACCCGUGA") == "MAGDP"

    def test_translate_unknown_codon_becomes_X(self):
        assert Translator().translate("ATGNNNTGA") == "MX"

    def test_invalid_frame(self):
        with pytest.raises(ValueError):
            Translator().translate("ATGC", frame=4)

    def test_invalid_nucleotide(self):
        with pytest.raises(InvalidSequenceError):
            Translator().translate("ATGCZ")


class TestCodonUsage:
    """Codon usage tests."""

    def test_analyze(self):
        codons = CodonUsage().analyze("ATGATGATG")
        assert len(codons) == 1
        assert codons[0].sequence == "ATG"
        assert codons[0].count == 3

    def test_rscu(self):
        rscu = CodonUsage().rscu("ATGATGATG")
        # Only ATG (Met, no synonyms) — RSCU should be 1.0
        assert rscu["ATG"] == 1.0

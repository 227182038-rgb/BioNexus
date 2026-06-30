"""Tests for biokit.kmers and biokit.motifs."""

from __future__ import annotations

from biokit.kmers import KmerCounter
from biokit.motifs import MotifFinder


class TestKmerCounter:
    """K-mer counter tests."""

    def test_count(self):
        # ATGCAT has kmers ATG(0), TGC(1), GCA(2), CAT(3) — 4 unique
        kmers = KmerCounter().count("ATGCAT", k=3)
        assert len(kmers) == 4
        seqs = [k.sequence for k in kmers]
        assert "ATG" in seqs
        assert "TGC" in seqs
        # Test kmer that appears multiple times: ATGCATATGC with k=3
        # kmers: ATG, TGC, GCA, CAT, ATA, TAT, ATG → ATG appears at 0 and 7
        kmers2 = KmerCounter().count("ATGCATATGC", k=3)
        atg = next(k for k in kmers2 if k.sequence == "ATG")
        assert atg.count == 2

    def test_count_with_positions(self):
        # ATGCATATGC: ATG at positions 0 and 6 (length 10, k=3, indices 0..7)
        positions = KmerCounter().count_with_positions("ATGCATATGC", k=3)
        assert positions["ATG"] == [0, 6]

    def test_k_too_large(self):
        assert KmerCounter().count("AT", k=10) == []


class TestMotifFinder:
    """Motif finder tests."""

    def test_find(self):
        motif = MotifFinder().find("ATGCATGCATGC", "ATGC")
        assert motif.count == 3
        assert motif.positions == [0, 4, 8]

    def test_find_no_match(self):
        motif = MotifFinder().find("ATGC", "GGGG")
        assert motif.count == 0

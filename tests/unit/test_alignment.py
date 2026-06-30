"""Tests for biokit.alignment."""

from __future__ import annotations

from biokit.alignment import GotohAligner, NeedlemanWunsch, SmithWaterman


class TestNeedlemanWunsch:
    """Needleman-Wunsch global alignment tests."""

    def test_identical_sequences(self):
        result = NeedlemanWunsch(match=1, mismatch=-1, gap=-2).align("ATGC", "ATGC")
        assert result.matches == 4
        assert result.mismatches == 0
        assert result.gaps == 0
        assert result.identity == 100.0
        assert result.aligned_seq1 == "ATGC"
        assert result.aligned_seq2 == "ATGC"

    def test_with_gaps(self):
        result = NeedlemanWunsch(match=1, mismatch=-1, gap=-2).align("GATTACA", "GCATGCU")
        assert result.length > 0
        assert result.matches > 0


class TestSmithWaterman:
    """Smith-Waterman local alignment tests."""

    def test_local_alignment(self):
        result = SmithWaterman(match=2, mismatch=-1, gap=-2).align("ACGTACGT", "ACGT")
        assert result.matches > 0
        assert "ACGT" in result.aligned_seq1


class TestGotoh:
    """Gotoh affine-gap alignment tests."""

    def test_basic(self):
        result = GotohAligner(match=1, mismatch=-1, gap_open=-5, gap_extend=-1).align(
            "ACGTACGT", "ACGTACGT"
        )
        assert result.matches > 0

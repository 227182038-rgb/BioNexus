"""Tests for biokit.assembly."""

from __future__ import annotations

import pytest
from biokit.assembly import DeBruijnAssembler, OverlapAssembler, assembly_gc, l50, n50, n90
from biokit.exceptions import AssemblyError, InvalidSequenceError
from biokit.utils.io_utils import make_record


def test_n50():
    assert n50([100, 200, 300, 400]) == 300
    assert n50([10]) == 10
    assert n50([]) == 0


def test_l50():
    assert l50([100, 200, 300, 400]) == 2
    assert l50([10]) == 1
    assert l50([]) == 0


def test_n90():
    # N90 = smallest contig whose cumulative length ≥ 90% of total
    # total = 1000, 90% = 900. Sorted desc: [400, 300, 200, 100]
    # cumulative: 400, 700, 900 → first ≥ 900 is 200
    assert n90([100, 200, 300, 400]) == 200


def test_debruijn_assembles_simple_genome():
    reads = ["ATGGCAGGTGAC", "GCAGGTGACCCG", "GGTGACCCGTTGA"]
    result = DeBruijnAssembler(k=5).assemble(reads)
    assert len(result.contigs) >= 1
    contig_seqs = [str(c.seq) for c in result.contigs]
    assert any("ATGGCAGGTGACCCGTTGA" in s for s in contig_seqs)


def test_debruijn_invalid_k():
    with pytest.raises(AssemblyError):
        DeBruijnAssembler(k=1)


def test_debruijn_invalid_dna():
    with pytest.raises(InvalidSequenceError):
        DeBruijnAssembler(k=3).assemble(["ATGCX"])


def test_overlap_assembler_basic():
    reads = ["ATGGCAGGTGAC", "CAGGTGACCCGTTGA"]
    result = OverlapAssembler(min_overlap=5).assemble(reads)
    assert len(result.contigs) == 1
    assert str(result.contigs[0].seq) == "ATGGCAGGTGACCCGTTGA"


def test_assembly_gc():
    contigs = [make_record("ATGC", "1"), make_record("ATGC", "2")]
    assert assembly_gc(contigs) == 0.5

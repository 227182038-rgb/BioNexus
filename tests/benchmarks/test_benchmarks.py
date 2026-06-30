"""Performance benchmarks for hot paths.

Run with:
    pytest tests/benchmarks/ --benchmark-only

Note on coverage
----------------
Coverage for the project is computed by the **full test suite** via the
``--cov=biokit`` flag in ``pyproject.toml``'s ``[tool.pytest.ini_options]
addopts``. The benchmark tests below are *not* intended to drive coverage on
their own — they only run when ``--benchmark-only`` is passed (which deselects
the regular tests). When running the full suite normally (no
``--benchmark-only``), pytest-benchmark skips the benchmark fixtures and the
``benchmark`` callable falls through to a plain function call, so the body of
each benchmark test still executes and contributes to coverage.

To confirm coverage is from the full suite, run:
    pytest --cov=biokit --cov-report=term
and check that the test count matches the full suite (153+ tests), not just
the 4 benchmarks in this file.
"""

from __future__ import annotations

import random
from collections.abc import Callable

from biokit.alignment import NeedlemanWunsch
from biokit.assembly import DeBruijnAssembler, n50
from biokit.sequence import DNA

# ---------------------------------------------------------------------------
# Deterministic pseudo-random DNA generation
# ---------------------------------------------------------------------------

#: Fixed RNG seed for reproducible benchmarks. Changing this invalidates
#: any benchmark baselines recorded with ``pytest-benchmark --benchmark-save``.
_BENCHMARK_SEED = 20250101

#: Canonical DNA bases only (no IUPAC ambiguity codes) so that the assembler's
#: ``validate_dna()`` call always succeeds.
_DNA_BASES = "ACGT"


def _make_dna(length: int, rng: random.Random) -> str:
    """Generate ``length`` nt of pseudo-random DNA using ``rng``.

    Parameters
    ----------
    length : int
        Number of nucleotides to generate. Must be ≥ 0.
    rng : random.Random
        A seeded RNG instance for reproducibility.

    Returns
    -------
    str
        A DNA string of length ``length`` containing only ``A``/``C``/``G``/``T``.
    """
    if length < 0:
        raise ValueError(f"length must be ≥ 0, got {length}")
    return "".join(rng.choice(_DNA_BASES) for _ in range(length))


def _make_overlapping_reads(
    genome: str,
    read_length: int,
    step: int,
    rng: random.Random,
) -> list[str]:
    """Slice ``genome`` into overlapping reads with realistic step and noise.

    Mimics short-read sequencing: each read is a window of ``read_length``
    nucleotides starting every ``step`` positions along the genome. A small
    per-read substitution rate (1 %) is applied so the assembler also has to
    deal with realistic sequencing error.

    Parameters
    ----------
    genome : str
        Backbone genome to slice.
    read_length : int
        Length of each read in nucleotides.
    step : int
        Distance between the start of consecutive reads. Must be < read_length
        for reads to overlap.
    rng : random.Random
        Seeded RNG for the per-read noise.

    Returns
    -------
    list[str]
        Overlapping reads covering ``genome``.
    """
    if step >= read_length:
        raise ValueError(f"step ({step}) must be < read_length ({read_length}) so reads overlap")
    reads: list[str] = []
    for start in range(0, max(0, len(genome) - read_length + 1), step):
        read = list(genome[start : start + read_length])
        # 1% per-base substitution error — keeps the assembler honest
        for i in range(len(read)):
            if rng.random() < 0.01:
                original = read[i]
                alternatives = [b for b in _DNA_BASES if b != original]
                read[i] = rng.choice(alternatives)
        reads.append("".join(read))
    return reads


# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------


def test_needleman_wunsch_100bp(benchmark: Callable) -> None:
    """Benchmark Needleman-Wunsch on two 100 bp identical sequences."""
    seq1 = "ATGCATGCAT" * 10
    seq2 = "ATGCATGCAT" * 10
    result = benchmark(NeedlemanWunsch().align, seq1, seq2)
    assert result.matches == 100


def test_debruijn_assembly_1000_reads(benchmark: Callable) -> None:
    """Benchmark De Bruijn assembly on 1000 biologically valid synthetic reads.

    Generates a pseudo-random genome with a fixed-seed RNG, then slices it
    into 1000 overlapping 50-nt reads with a 1% per-base substitution error
    rate. This exercises the assembler with realistic input rather than
    artificial sequences that violate the DNA alphabet.

    Read count formula: ``floor((genome_length - read_length) / step) + 1``.
    With ``read_length=50`` and ``step=5``, ``genome_length=5045`` yields
    exactly 1000 reads.
    """
    rng = random.Random(_BENCHMARK_SEED)
    genome = _make_dna(length=5045, rng=rng)
    reads = _make_overlapping_reads(
        genome,
        read_length=50,
        step=5,
        rng=rng,
    )
    # Sanity-check the fixture: every read must be valid DNA and we must have
    # produced the expected number of reads.
    assert len(reads) == 1000, f"expected 1000 reads, got {len(reads)}"
    for read in reads:
        # ``DNA(...)`` raises InvalidSequenceError on bad input — this is the
        # same validator the assembler uses, so it catches the original bug.
        DNA(read)  # would raise if any non-ACGT character slipped in

    result = benchmark(DeBruijnAssembler(k=15).assemble, reads)
    assert result.num_contigs > 0


def test_dna_reverse_complement_1kb(benchmark: Callable) -> None:
    """Benchmark reverse complement on a 1 kb sequence."""
    seq = "ATGCATGCAT" * 100
    rc = benchmark(lambda s: DNA(s).reverse_complement().sequence, seq)
    assert len(rc) == 1000


def test_n50_large(benchmark: Callable) -> None:
    """Benchmark N50 on 10k contigs of increasing length."""
    contigs = list(range(1, 10001))
    result = benchmark(n50, contigs)
    assert result > 0

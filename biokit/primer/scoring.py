"""Primer scoring and self-complementarity."""

from __future__ import annotations

from biokit.primer.candidate import PrimerCandidate
from biokit.primer.melting_temp import tm_nearest_neighbor
from biokit.sequence.dna import DNA
from biokit.statistics.sequence_stats import gc_fraction

DEFAULT_TM_TARGET = 60.0


def gc_clamp_score(sequence: str) -> int:
    """Number of G/C bases in the last 5 nucleotides."""
    return sum(1 for b in sequence[-5:] if b in "GC")


def max_self_complementarity(sequence: str) -> int:
    """Longest self-complementary stretch (proxy for hairpin/dimer)."""
    seq = sequence.upper()
    rc = DNA(seq).reverse_complement().sequence
    best = 0
    for i in range(len(seq)):
        for j in range(len(rc)):
            k = 0
            while i + k < len(seq) and j + k < len(rc) and seq[i + k] == rc[j + k]:
                k += 1
            best = max(best, k)
    return best


def has_hairpin(sequence: str, min_stem: int = 4) -> bool:
    """Detect whether the primer can fold into a hairpin."""
    return max_self_complementarity(sequence) >= min_stem


def score_primer(
    primer: PrimerCandidate,
    tm_target: float = DEFAULT_TM_TARGET,
    gc_min: float = 0.4,
    gc_max: float = 0.6,
    max_self_comp: int = 4,
) -> float:
    """Score a primer; higher is better."""
    score = 100.0
    score -= abs(primer.tm - tm_target) * 2.0
    if primer.gc < gc_min or primer.gc > gc_max:
        score -= 30.0
    else:
        score += 10.0
    if primer.self_comp > max_self_comp:
        score -= (primer.self_comp - max_self_comp) * 15.0
    if 1 <= primer.gc_clamp <= 3:
        score += 5.0
    elif primer.gc_clamp == 0:
        score -= 5.0
    else:
        score -= 3.0
    return score


def _build_candidate(
    sequence: str,
    start: int,
    strand: str,
    tm_target: float,
) -> PrimerCandidate:
    tm = tm_nearest_neighbor(sequence)
    gc = gc_fraction(sequence)
    self_comp = max_self_complementarity(sequence)
    clamp = gc_clamp_score(sequence)
    cand = PrimerCandidate(
        sequence=sequence,
        start=start,
        end=start + len(sequence) - 1,
        strand=strand,
        tm=tm,
        gc=gc,
        self_comp=self_comp,
        gc_clamp=clamp,
    )
    object.__setattr__(cand, "score", score_primer(cand, tm_target=tm_target))
    return cand


__all__ = [
    "DEFAULT_TM_TARGET",
    "_build_candidate",
    "gc_clamp_score",
    "has_hairpin",
    "max_self_complementarity",
    "score_primer",
]

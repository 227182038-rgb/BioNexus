"""Allele/genotype frequency and heterozygosity calculations."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from biokit.exceptions import PopGenError
from biokit.popgen.models import AlleleStats, Genotype


def allele_frequencies(genotypes: Iterable[Genotype]) -> dict[str, float]:
    """Compute allele frequencies from genotypes.

    Examples
    --------
    >>> allele_frequencies([("A", "A"), ("A", "a"), ("a", "a")])
    {'A': 0.5, 'a': 0.5}
    """
    counts: Counter[str] = Counter()
    total = 0
    for gt in genotypes:
        if len(gt) != 2:
            raise PopGenError(f"genotype must be a 2-tuple, got {gt!r}")
        counts[gt[0]] += 1
        counts[gt[1]] += 1
        total += 2
    if total == 0:
        return {}
    return {a: c / total for a, c in counts.items()}


def genotype_frequencies(genotypes: Iterable[Genotype]) -> dict[Genotype, float]:
    """Compute genotype frequencies (normalised so smaller allele first)."""
    counts: Counter[Genotype] = Counter()
    total = 0
    for gt in genotypes:
        # Normalise so the smaller allele comes first.
        a1, a2 = sorted(gt)
        counts[(a1, a2)] += 1
        total += 1
    if total == 0:
        return {}
    return {gt: c / total for gt, c in counts.items()}


def observed_heterozygosity(genotypes: Iterable[Genotype]) -> float:
    """Observed heterozygosity (Ho)."""
    genotypes = list(genotypes)
    if not genotypes:
        return 0.0
    return sum(1 for gt in genotypes if gt[0] != gt[1]) / len(genotypes)


def expected_heterozygosity(genotypes: Iterable[Genotype]) -> float:
    """Expected heterozygosity (He) under HWE: ``1 - Σ p_i²``."""
    freqs = allele_frequencies(genotypes)
    return 1.0 - sum(p * p for p in freqs.values())


def allele_stats(genotypes: Iterable[Genotype]) -> AlleleStats:
    """Combined summary statistics for a single locus."""
    genotypes = list(genotypes)
    freqs = allele_frequencies(genotypes)
    return AlleleStats(
        allele_freqs=freqs,
        observed_heterozygosity=observed_heterozygosity(genotypes),
        expected_heterozygosity=expected_heterozygosity(genotypes),
        num_genotypes=len(genotypes),
        num_alleles=len(freqs),
    )


__all__ = [
    "allele_frequencies",
    "allele_stats",
    "expected_heterozygosity",
    "genotype_frequencies",
    "observed_heterozygosity",
]

"""Population genetics data models."""

from __future__ import annotations

from dataclasses import dataclass

Genotype = tuple[str, str]


@dataclass(frozen=True)
class AlleleStats:
    """Summary statistics for a single locus."""

    allele_freqs: dict[str, float]
    observed_heterozygosity: float
    expected_heterozygosity: float
    num_genotypes: int
    num_alleles: int


__all__ = ["AlleleStats", "Genotype"]

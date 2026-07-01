"""Linkage disequilibrium: D' and r²."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from biokit.exceptions import PopGenError
from biokit.popgen.frequencies import allele_frequencies
from biokit.popgen.models import Genotype


def linkage_disequilibrium(
    genotypes_a: Sequence[Genotype],
    genotypes_b: Sequence[Genotype],
) -> tuple[float, float]:
    """Compute D' and r² for two loci.

    Returns
    -------
    tuple[float, float]
        ``(D_prime, r_squared)``.
    """
    if len(genotypes_a) != len(genotypes_b):
        raise PopGenError("locus genotype lists must have the same length")
    n = len(genotypes_a)
    if n == 0:
        return 0.0, 0.0
    fa = allele_frequencies(genotypes_a)
    fb = allele_frequencies(genotypes_b)
    if not fa or not fb:
        return 0.0, 0.0
    a = max(fa, key=lambda k: fa[k])
    b = max(fb, key=lambda k: fb[k])
    pa = fa[a]
    pb = fb[b]
    xa = [sum(1 for x in gt if x == a) / 2.0 for gt in genotypes_a]
    xb = [sum(1 for x in gt if x == b) / 2.0 for gt in genotypes_b]
    xa_arr = np.array(xa)
    xb_arr = np.array(xb)
    pab = float((xa_arr * xb_arr).mean())
    d = pab - pa * pb
    if d >= 0:
        d_max = min(pa * (1 - pb), (1 - pa) * pb)
    else:
        d_max = min(pa * pb, (1 - pa) * (1 - pb))
    d_prime = d / d_max if d_max != 0 else 0.0
    denom = pa * (1 - pa) * pb * (1 - pb)
    r2 = (d * d) / denom if denom != 0 else 0.0
    return float(d_prime), float(r2)


__all__ = ["linkage_disequilibrium"]

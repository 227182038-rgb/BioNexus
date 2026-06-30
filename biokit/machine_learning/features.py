"""Feature extraction from biological sequences."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from biokit.exceptions import ValidationError


def kmer_features(
    sequences: Sequence[str],
    k: int = 3,
    alphabet: str = "ACGT",
) -> NDArray[np.float64]:
    """Build a k-mer frequency feature matrix.

    Each row is the k-mer composition of one sequence, with one column per
    possible k-mer over ``alphabet``.

    Parameters
    ----------
    sequences : sequence of str
        DNA sequences.
    k : int, optional
        K-mer size (default 3).
    alphabet : str, optional
        Alphabet (default ``"ACGT"``).

    Returns
    -------
    numpy.ndarray
        Shape ``(n_sequences, n_kmers)``.

    Examples
    --------
    >>> X = kmer_features(["AAACCC", "GGGTTT"], k=2)
    >>> X.shape
    (2, 16)
    """
    if k < 1:
        raise ValidationError("k must be ≥ 1")
    from itertools import product

    kmers = ["".join(p) for p in product(alphabet, repeat=k)]
    kmer_idx = {km: i for i, km in enumerate(kmers)}
    out = np.zeros((len(sequences), len(kmers)), dtype=float)
    for i, seq in enumerate(sequences):
        seq_u = seq.upper()
        counts: Counter[str] = Counter()
        for j in range(len(seq_u) - k + 1):
            km = seq_u[j : j + k]
            if all(c in alphabet for c in km):
                counts[km] += 1
        total = sum(counts.values()) or 1
        for km, c in counts.items():
            out[i, kmer_idx[km]] = c / total
    return out


def gc_content_features(sequences: Sequence[str]) -> NDArray[np.float64]:
    """Return GC content per sequence as a column vector."""
    from biokit.statistics.sequence_stats import gc_fraction

    return np.array([[gc_fraction(s)] for s in sequences])


def sequence_length_features(sequences: Sequence[str]) -> NDArray[np.int32]:
    """Return sequence lengths as an int column vector."""
    return np.array([[len(s)] for s in sequences], dtype=np.int32)


__all__ = ["gc_content_features", "kmer_features", "sequence_length_features"]

"""Nucleotide composition utilities."""

from __future__ import annotations

from collections import Counter


def nucleotide_counts(sequence: str) -> dict[str, int]:
    """Count the occurrence of each character in ``sequence``.

    Parameters
    ----------
    sequence : str
        Nucleotide or protein sequence.

    Returns
    -------
    dict[str, int]
        Mapping from character to count.

    Examples
    --------
    >>> nucleotide_counts("AATGC")
    {'A': 2, 'T': 1, 'G': 1, 'C': 1}
    """
    return dict(Counter(sequence.upper()))


__all__ = ["nucleotide_counts"]

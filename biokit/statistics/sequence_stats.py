"""Sequence statistics functions."""

from __future__ import annotations

import math
from collections import Counter


def gc_fraction(sequence: str) -> float:
    """Compute the GC fraction of a sequence as a number in ``[0, 1]``.

    Parameters
    ----------
    sequence : str
        DNA or RNA sequence.

    Returns
    -------
    float
        GC fraction between 0 and 1. Empty sequences return 0.0.

    Examples
    --------
    >>> gc_fraction("ATGC")
    0.5
    >>> gc_fraction("GGCC")
    1.0
    >>> gc_fraction("ATAT")
    0.0
    >>> gc_fraction("")
    0.0
    """
    if not sequence:
        return 0.0
    seq = sequence.upper()
    gc = seq.count("G") + seq.count("C")
    return gc / len(seq)


def gc_percentage(sequence: str) -> float:
    """Compute the GC percentage (0–100).

    Parameters
    ----------
    sequence : str
        DNA or RNA sequence.

    Returns
    -------
    float
        GC percentage in [0, 100].

    Examples
    --------
    >>> gc_percentage("ATGC")
    50.0
    """
    return gc_fraction(sequence) * 100.0


# Approximate monoisotopic masses (Da) for nucleotide monophosphates
# in a single-stranded sequence. Used by :func:`molecular_weight_daltons`.
_NUCLEOTIDE_MW: dict[str, float] = {
    "A": 331.2218,
    "T": 322.2085,
    "U": 308.2085,
    "G": 347.2212,
    "C": 307.1971,
}

# Approximate average masses (Da) for amino acid residues.
_AMINO_ACID_MW: dict[str, float] = {
    "A": 71.0788,
    "R": 156.1875,
    "N": 114.1038,
    "D": 115.0886,
    "C": 103.1388,
    "E": 129.1155,
    "Q": 128.1307,
    "G": 57.0519,
    "H": 137.1411,
    "I": 113.1594,
    "L": 113.1594,
    "K": 128.1741,
    "M": 131.1926,
    "F": 147.1766,
    "P": 97.1167,
    "S": 87.0782,
    "T": 101.1051,
    "W": 186.2132,
    "Y": 163.1760,
    "V": 99.1326,
    "X": 110.0,  # unknown — use average
}


def molecular_weight_daltons(sequence: str) -> float:
    """Approximate molecular weight of a single-stranded sequence in Daltons.

    Detects DNA/RNA vs protein heuristically (presence of T → DNA; U → RNA;
    otherwise protein). Water loss is ignored for protein residues.

    Parameters
    ----------
    sequence : str
        Biological sequence.

    Returns
    -------
    float
        Molecular weight in Daltons.

    Examples
    --------
    >>> molecular_weight_daltons("ATGC") > 1000
    True
    >>> molecular_weight_daltons("MAGDPV") > 0
    True
    """
    if not sequence:
        return 0.0
    seq = sequence.upper()
    # Protein if any char is not a nucleotide
    if all(c in _NUCLEOTIDE_MW for c in seq):
        # Subtract water for each phosphodiester bond
        n = len(seq)
        return (
            sum(_NUCLEOTIDE_MW[c] for c in seq) - 61.96 * (n - 1)
            if n > 1
            else sum(_NUCLEOTIDE_MW[c] for c in seq)
        )
    # Protein
    return sum(_AMINO_ACID_MW.get(c, _AMINO_ACID_MW["X"]) for c in seq)


def sequence_complexity(sequence: str) -> float:
    """Compute the Shannon entropy of a sequence (in bits).

    A low-complexity sequence (e.g. ``AAAAAA``) has entropy close to 0,
    while a maximally diverse sequence has entropy close to ``log2(alphabet_size)``.

    Parameters
    ----------
    sequence : str
        Biological sequence.

    Returns
    -------
    float
        Shannon entropy in bits.

    Examples
    --------
    >>> sequence_complexity("AAAAAA")
    0.0
    >>> sequence_complexity("ACGT") > 1.9
    True
    """
    if not sequence:
        return 0.0
    counts = Counter(sequence.upper())
    total = sum(counts.values())
    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


__all__ = [
    "gc_fraction",
    "gc_percentage",
    "molecular_weight_daltons",
    "sequence_complexity",
]

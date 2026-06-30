"""Protein sequence type."""

from __future__ import annotations

from biokit.constants import PROTEIN_ALPHABET
from biokit.sequence.sequence import BioSequence


class Protein(BioSequence):
    """A protein sequence.

    Parameters
    ----------
    sequence : str
        Protein sequence (case-insensitive, will be upper-cased).
    id : str, optional
        Sequence identifier.
    description : str, optional
        Human-readable description.

    Examples
    --------
    >>> protein = Protein("MAGDPV")
    >>> protein.length
    6
    >>> protein.molecular_weight > 0
    True
    """

    alphabet = PROTEIN_ALPHABET


__all__ = ["Protein"]

"""Sequence validation utilities."""

from __future__ import annotations

from biokit.constants import DNA_ALPHABET, PROTEIN_ALPHABET, RNA_ALPHABET
from biokit.exceptions import InvalidSequenceError


def is_dna(sequence: str) -> bool:
    """Return ``True`` if ``sequence`` contains only canonical DNA bases.

    Examples
    --------
    >>> is_dna("ATGC")
    True
    >>> is_dna("AUGC")
    False
    """
    return all(base in "ATGC" for base in sequence.upper())


def is_rna(sequence: str) -> bool:
    """Return ``True`` if ``sequence`` contains only canonical RNA bases.

    Examples
    --------
    >>> is_rna("AUGC")
    True
    >>> is_rna("ATGC")
    False
    """
    return all(base in "ACGU" for base in sequence.upper())


def is_protein(sequence: str) -> bool:
    """Return ``True`` if ``sequence`` contains only amino acid codes."""
    return all(aa in PROTEIN_ALPHABET for aa in sequence.upper())


def validate_dna(sequence: str) -> None:
    """Validate that ``sequence`` only contains IUPAC DNA symbols.

    Raises
    ------
    InvalidSequenceError
        If the sequence contains characters outside the DNA alphabet.
    """
    invalid = set(sequence.upper()) - DNA_ALPHABET
    if invalid:
        raise InvalidSequenceError(f"invalid DNA character(s): {invalid!r}")


def validate_rna(sequence: str) -> None:
    """Validate that ``sequence`` only contains IUPAC RNA symbols."""
    invalid = set(sequence.upper()) - RNA_ALPHABET
    if invalid:
        raise InvalidSequenceError(f"invalid RNA character(s): {invalid!r}")


def validate_protein(sequence: str) -> None:
    """Validate that ``sequence`` only contains IUPAC protein symbols."""
    invalid = set(sequence.upper()) - PROTEIN_ALPHABET
    if invalid:
        raise InvalidSequenceError(f"invalid protein character(s): {invalid!r}")


__all__ = [
    "is_dna",
    "is_protein",
    "is_rna",
    "validate_dna",
    "validate_protein",
    "validate_rna",
]

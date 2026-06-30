"""Substitution matrices and scoring helpers."""

from __future__ import annotations

from collections.abc import Callable

#: BLOSUM62 substitution matrix (subset; full matrix in production).
BLOSUM62: dict[tuple[str, str], int] = {
    ("A", "A"): 4,
    ("R", "R"): 5,
    ("N", "N"): 6,
    ("D", "D"): 6,
    ("C", "C"): 9,
    ("Q", "Q"): 5,
    ("E", "E"): 5,
    ("G", "G"): 6,
    ("H", "H"): 8,
    ("I", "I"): 4,
    ("L", "L"): 4,
    ("K", "K"): 5,
    ("M", "M"): 5,
    ("F", "F"): 6,
    ("P", "P"): 7,
    ("S", "S"): 4,
    ("T", "T"): 5,
    ("W", "W"): 11,
    ("Y", "Y"): 7,
    ("V", "V"): 4,
    ("A", "R"): -1,
    ("A", "N"): -2,
    ("A", "D"): -2,
    ("A", "C"): 0,
    ("A", "Q"): -1,
    ("A", "E"): -1,
    ("A", "G"): 0,
    ("A", "H"): -2,
    ("A", "I"): -1,
    ("A", "L"): -1,
    ("A", "K"): -1,
    ("A", "M"): -1,
    ("A", "F"): -2,
    ("A", "P"): -1,
    ("A", "S"): 1,
    ("A", "T"): 0,
    ("A", "W"): -3,
    ("A", "Y"): -2,
    ("A", "V"): 0,
}

#: PAM30 substitution matrix (subset).
PAM30: dict[tuple[str, str], int] = {
    ("A", "A"): 6,
    ("R", "R"): 8,
    ("N", "N"): 10,
    ("D", "D"): 10,
    ("C", "C"): 12,
    ("Q", "Q"): 10,
    ("E", "E"): 10,
    ("G", "G"): 8,
    ("H", "H"): 10,
    ("I", "I"): 5,
    ("L", "L"): 6,
    ("K", "K"): 6,
    ("M", "M"): 6,
    ("F", "F"): 9,
    ("P", "P"): 10,
    ("S", "S"): 6,
    ("T", "T"): 6,
    ("W", "W"): 17,
    ("Y", "Y"): 10,
    ("V", "V"): 4,
}


def match_mismatch_scoring(match: int = 1, mismatch: int = -1) -> Callable[[str, str], int]:
    """Return a scoring function for simple match/mismatch scoring.

    Parameters
    ----------
    match : int, optional
        Score for matching characters (default 1).
    mismatch : int, optional
        Score for mismatching characters (default -1).

    Returns
    -------
    callable
        A function ``f(a, b) -> int``.
    """

    def score(a: str, b: str) -> int:
        return match if a == b else mismatch

    return score


__all__ = ["BLOSUM62", "PAM30", "match_mismatch_scoring"]

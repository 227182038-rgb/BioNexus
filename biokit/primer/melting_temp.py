"""Melting temperature estimators."""

from __future__ import annotations

import math

from biokit.exceptions import PrimerError

_NN_DH: dict[str, float] = {
    "AA": -7.9,
    "TT": -7.9,
    "AT": -7.2,
    "TA": -7.2,
    "CA": -8.5,
    "TG": -8.5,
    "GT": -8.4,
    "AC": -8.4,
    "CT": -7.8,
    "AG": -7.8,
    "GA": -8.2,
    "TC": -8.2,
    "CG": -10.6,
    "GC": -9.8,
    "GG": -8.0,
    "CC": -8.0,
}
_NN_DS: dict[str, float] = {
    "AA": -22.2,
    "TT": -22.2,
    "AT": -20.4,
    "TA": -21.3,
    "CA": -22.7,
    "TG": -22.7,
    "GT": -22.4,
    "AC": -22.4,
    "CT": -21.0,
    "AG": -21.0,
    "GA": -22.2,
    "TC": -22.2,
    "CG": -27.2,
    "GC": -24.8,
    "GG": -19.9,
    "CC": -19.9,
}
_INIT_DH = 0.2
_INIT_DS = -5.7
_INIT_DS_TERMINAL_AT = -1.4


def tm_wallace(sequence: str) -> float:
    """Wallace-rule Tm: ``2 * (A+T) + 4 * (G+C)``.

    Examples
    --------
    >>> tm_wallace("ATGCATGC")
    24.0
    """
    seq = sequence.upper()
    at = seq.count("A") + seq.count("T")
    gc = seq.count("G") + seq.count("C")
    return float(2 * at + 4 * gc)


def tm_gc(sequence: str, na_conc: float = 50.0) -> float:
    """GC-based Tm with salt correction."""
    seq = sequence.upper()
    if not seq:
        return 0.0
    gc = (seq.count("G") + seq.count("C")) / len(seq) * 100
    return 81.5 + 16.6 * math.log10(na_conc / 1000.0) + 0.41 * gc - 600.0 / len(seq)


def tm_nearest_neighbor(
    sequence: str,
    na_conc: float = 50.0,
    primer_conc: float = 250.0,
) -> float:
    """SantaLucia (1998) nearest-neighbour Tm.

    Examples
    --------
    >>> round(tm_nearest_neighbor("GTAAAACGACGGCCAGT"), 1) > 40.0
    True
    """
    seq = sequence.upper()
    if len(seq) < 2:
        raise PrimerError("sequence must be ≥ 2 nt for nearest-neighbour Tm")
    dh = _INIT_DH
    ds = _INIT_DS
    if seq[0] in "AT":
        ds += _INIT_DS_TERMINAL_AT
    if seq[-1] in "AT":
        ds += _INIT_DS_TERMINAL_AT
    for i in range(len(seq) - 1):
        pair = seq[i : i + 2]
        if pair not in _NN_DH:
            raise PrimerError(f"unsupported NN pair: {pair!r}")
        dh += _NN_DH[pair]
        ds += _NN_DS[pair]
    r = 1.987
    dh_cal = dh * 1000.0
    ct = primer_conc * 1e-9
    tm_k = dh_cal / (ds + r * math.log(ct / 4.0))
    tm_c = tm_k - 273.15
    tm_c += 16.6 * math.log10(na_conc / 1000.0)
    return tm_c


__all__ = ["tm_gc", "tm_nearest_neighbor", "tm_wallace"]

"""Sliding-window primer designer."""

from __future__ import annotations

from biokit.exceptions import PrimerError
from biokit.primer.candidate import PrimerCandidate
from biokit.primer.scoring import DEFAULT_TM_TARGET, _build_candidate
from biokit.sequence.dna import DNA
from biokit.sequence.validation import validate_dna

DEFAULT_PRIMER_LENGTH = 20


def design_primer(
    template: str,
    length: int = DEFAULT_PRIMER_LENGTH,
    tm_target: float = DEFAULT_TM_TARGET,
    gc_min: float = 0.4,
    gc_max: float = 0.6,
    max_self_comp: int = 4,
    min_score: float = 0.0,
    scan_reverse: bool = True,
) -> list[PrimerCandidate]:
    """Design forward (and optionally reverse) primers for ``template``.

    Examples
    --------
    >>> primers = design_primer("ATGGCAGGTGACCCGTTGACCGTACGTAACGCATGCAGT")
    >>> all(p.gc >= 0.0 for p in primers)
    True
    """
    validate_dna(template)
    template = template.upper()
    if length < 8 or length > len(template):
        raise PrimerError(f"length must be between 8 and template length ({len(template)})")
    candidates: list[PrimerCandidate] = []
    for i in range(len(template) - length + 1):
        window = template[i : i + length]
        cand = _build_candidate(window, start=i + 1, strand="+", tm_target=tm_target)
        if cand.gc < gc_min or cand.gc > gc_max:
            continue
        if cand.self_comp > max_self_comp:
            continue
        if cand.score >= min_score:
            candidates.append(cand)
    if scan_reverse:
        rc_template = DNA(template).reverse_complement().sequence
        for i in range(len(rc_template) - length + 1):
            window = rc_template[i : i + length]
            cand = _build_candidate(
                window,
                start=len(template) - i - length + 1,
                strand="-",
                tm_target=tm_target,
            )
            if cand.gc < gc_min or cand.gc > gc_max:
                continue
            if cand.self_comp > max_self_comp:
                continue
            if cand.score >= min_score:
                candidates.append(cand)
    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates


__all__ = ["DEFAULT_PRIMER_LENGTH", "design_primer"]

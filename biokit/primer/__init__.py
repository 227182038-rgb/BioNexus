"""Primer design: Tm estimators, scoring, sliding-window designer."""

from __future__ import annotations

from biokit.primer.candidate import PrimerCandidate
from biokit.primer.designer import DEFAULT_PRIMER_LENGTH, design_primer
from biokit.primer.melting_temp import tm_gc, tm_nearest_neighbor, tm_wallace
from biokit.primer.scoring import (
    DEFAULT_TM_TARGET,
    gc_clamp_score,
    has_hairpin,
    max_self_complementarity,
    score_primer,
)

__all__ = [
    "DEFAULT_PRIMER_LENGTH",
    "DEFAULT_TM_TARGET",
    "PrimerCandidate",
    "design_primer",
    "gc_clamp_score",
    "has_hairpin",
    "max_self_complementarity",
    "score_primer",
    "tm_gc",
    "tm_nearest_neighbor",
    "tm_wallace",
]

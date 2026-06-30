"""CRISPR sgRNA design and off-target search."""

from __future__ import annotations

from biokit.crispr.constants import (
    DEFAULT_GUIDE_LENGTH,
    DEFAULT_MAX_MISMATCHES,
    DEFAULT_PAM,
)
from biokit.crispr.designer import (
    annotate_guides,
    design_guides,
    find_off_targets,
    iter_guides,
    score_guide,
)
from biokit.crispr.models import GuideRNA, OffTarget

__all__ = [
    "DEFAULT_GUIDE_LENGTH",
    "DEFAULT_MAX_MISMATCHES",
    "DEFAULT_PAM",
    "GuideRNA",
    "OffTarget",
    "annotate_guides",
    "design_guides",
    "find_off_targets",
    "iter_guides",
    "score_guide",
]

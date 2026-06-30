"""Genome annotation: feature orchestration across GFF3/BED/GenBank."""

from __future__ import annotations

from biokit.annotation.feature import AnnotationFeature
from biokit.annotation.lookup import feature_children, features_by_type, features_in_range
from biokit.annotation.translate import translate_cds

__all__ = [
    "AnnotationFeature",
    "feature_children",
    "features_by_type",
    "features_in_range",
    "translate_cds",
]

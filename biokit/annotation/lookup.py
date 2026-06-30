"""Feature lookup utilities."""

from __future__ import annotations

from collections.abc import Iterable

from biokit.annotation.feature import AnnotationFeature


def features_by_type(features: Iterable[AnnotationFeature], ftype: str) -> list[AnnotationFeature]:
    """Return features of a given type (case-insensitive)."""
    target = ftype.lower()
    return [f for f in features if f.type.lower() == target]


def features_in_range(
    features: Iterable[AnnotationFeature],
    start: int,
    end: int,
    seqid: str | None = None,
) -> list[AnnotationFeature]:
    """Return features overlapping ``[start, end]`` (1-based, inclusive)."""
    out: list[AnnotationFeature] = []
    for feat in features:
        if seqid is not None and feat.seqid != seqid:
            continue
        if feat.end < start or feat.start > end:
            continue
        out.append(feat)
    return out


def feature_children(
    features: Iterable[AnnotationFeature], parent_id: str
) -> list[AnnotationFeature]:
    """Return features whose ``Parent`` attribute equals ``parent_id``."""
    return [f for f in features if f.attributes.get("Parent") == parent_id]


__all__ = ["feature_children", "features_by_type", "features_in_range"]

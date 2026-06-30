"""BLAST hit filtering."""

from __future__ import annotations

from collections.abc import Iterable

from biokit.blast.models import BlastHit, BlastRecord


def filter_hits(
    records: Iterable[BlastRecord],
    max_evalue: float = 1e-5,
    min_identity: float = 0.0,
) -> list[BlastRecord]:
    """Filter BLAST records by E-value and percent identity.

    Parameters
    ----------
    records : iterable of BlastRecord
        Records to filter.
    max_evalue : float, optional
        Maximum E-value (default 1e-5).
    min_identity : float, optional
        Minimum percent identity (default 0).

    Returns
    -------
    list[BlastRecord]
        Filtered records. Hits with no surviving HSPs are dropped.
    """
    out: list[BlastRecord] = []
    for record in records:
        kept_hits: list[BlastHit] = []
        for hit in record.hits:
            kept = [
                h for h in hit.hsps if h.evalue <= max_evalue and h.percent_identity >= min_identity
            ]
            if kept:
                kept_hits.append(
                    BlastHit(
                        subject_id=hit.subject_id,
                        subject_title=hit.subject_title,
                        subject_length=hit.subject_length,
                        hsps=kept,
                    )
                )
        if kept_hits:
            out.append(
                BlastRecord(
                    query_id=record.query_id,
                    query_length=record.query_length,
                    hits=kept_hits,
                )
            )
    return out


__all__ = ["filter_hits"]

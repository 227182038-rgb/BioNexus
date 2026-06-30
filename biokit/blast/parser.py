"""BLAST XML and tabular parsers."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Sequence
from pathlib import Path

from biokit.blast.models import HSP, BlastHit, BlastRecord
from biokit.exceptions import InvalidFormatError

DEFAULT_TABULAR_COLUMNS = (
    "qseqid",
    "sseqid",
    "pident",
    "length",
    "mismatch",
    "gapopen",
    "qstart",
    "qend",
    "sstart",
    "send",
    "evalue",
    "bitscore",
)


def _to_float(value: str | None, default: float = 0.0) -> float:
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _to_int(value: str | None, default: int = 0) -> int:
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def parse_blast_xml(path: str | Path) -> list[BlastRecord]:
    """Parse BLAST XML (``-outfmt 5``) into records.

    Raises
    ------
    InvalidFormatError
        If the file is missing or contains invalid XML.
    """
    p = Path(path)
    if not p.exists():
        raise InvalidFormatError(f"file not found: {p}")
    try:
        tree = ET.parse(str(p))
    except ET.ParseError as exc:
        raise InvalidFormatError(f"invalid BLAST XML: {exc}") from exc
    root = tree.getroot()
    records: list[BlastRecord] = []
    for iteration in root.findall(".//Iteration"):
        query_def = (iteration.findtext("Iteration_query-def") or "").strip()
        query_id = query_def.split()[0] if query_def else ""
        query_length = _to_int(iteration.findtext("Iteration_query-len"))
        hits: list[BlastHit] = []
        for hit_node in iteration.findall(".//Hit"):
            subject_id = (hit_node.findtext("Hit_id") or "").strip()
            subject_def = (hit_node.findtext("Hit_def") or "").strip()
            subject_len = _to_int(hit_node.findtext("Hit_len"))
            hsps: list[HSP] = []
            for hsp in hit_node.findall(".//Hsp"):
                hsps.append(
                    HSP(
                        query_id=query_id,
                        subject_id=subject_id,
                        query_start=_to_int(hsp.findtext("Hsp_query-from")),
                        query_end=_to_int(hsp.findtext("Hsp_query-to")),
                        subject_start=_to_int(hsp.findtext("Hsp_hit-from")),
                        subject_end=_to_int(hsp.findtext("Hsp_hit-to")),
                        query_seq=hsp.findtext("Hsp_qseq") or "",
                        subject_seq=hsp.findtext("Hsp_hseq") or "",
                        midline=hsp.findtext("Hsp_midline") or "",
                        score=_to_float(hsp.findtext("Hsp_bit-score")),
                        evalue=_to_float(hsp.findtext("Hsp_evalue"), float("inf")),
                        identity=_to_int(hsp.findtext("Hsp_identity")),
                        positives=_to_int(hsp.findtext("Hsp_positive"), -1),
                        gaps=_to_int(hsp.findtext("Hsp_gaps")),
                        alignment_length=_to_int(hsp.findtext("Hsp_align-len")),
                    )
                )
                if hsps[-1].positives < 0:
                    object.__setattr__(hsps[-1], "positives", hsps[-1].identity)
            hits.append(
                BlastHit(
                    subject_id=subject_id,
                    subject_title=subject_def,
                    subject_length=subject_len,
                    hsps=hsps,
                )
            )
        records.append(
            BlastRecord(
                query_id=query_id,
                query_length=query_length,
                hits=hits,
            )
        )
    return records


def parse_blast_tabular(
    path: str | Path,
    columns: Sequence[str] = DEFAULT_TABULAR_COLUMNS,
    comment_char: str | None = "#",
) -> list[BlastRecord]:
    """Parse BLAST tabular output (``-outfmt 6`` or ``7``)."""
    p = Path(path)
    if not p.exists():
        raise InvalidFormatError(f"file not found: {p}")
    records_by_query: dict[str, BlastRecord] = {}
    hits_by_subject: dict[tuple[str, str], BlastHit] = {}
    with p.open() as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            if not line or (comment_char and line.startswith(comment_char)):
                continue
            fields = line.split("\t")
            if len(fields) != len(columns):
                raise InvalidFormatError(
                    f"line {lineno}: expected {len(columns)} fields, got {len(fields)}"
                )
            row = dict(zip(columns, fields, strict=False))
            qid = row["qseqid"]
            sid = row["sseqid"]
            rec = records_by_query.setdefault(qid, BlastRecord(query_id=qid))
            key = (qid, sid)
            hit = hits_by_subject.get(key)
            if hit is None:
                hit = BlastHit(subject_id=sid)
                object.__setattr__(hit, "hsps", [])
                hits_by_subject[key] = hit
                rec.hits.append(hit)
            identity = round(_to_float(row.get("pident")) * _to_int(row.get("length")) / 100)
            hit.hsps.append(
                HSP(
                    query_id=qid,
                    subject_id=sid,
                    query_start=_to_int(row.get("qstart")),
                    query_end=_to_int(row.get("qend")),
                    subject_start=_to_int(row.get("sstart")),
                    subject_end=_to_int(row.get("send")),
                    score=_to_float(row.get("bitscore")),
                    evalue=_to_float(row.get("evalue"), float("inf")),
                    identity=identity,
                    positives=identity,
                    alignment_length=_to_int(row.get("length")),
                )
            )
    return list(records_by_query.values())


__all__ = ["DEFAULT_TABULAR_COLUMNS", "parse_blast_tabular", "parse_blast_xml"]

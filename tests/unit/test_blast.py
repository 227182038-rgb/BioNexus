"""Tests for biokit.blast."""

from __future__ import annotations

import pytest
from biokit.blast import (
    HSP,
    BlastHit,
    BlastRecord,
    filter_hits,
    parse_blast_tabular,
    parse_blast_xml,
    run_blast_local,
)
from biokit.exceptions import BlastError, InvalidFormatError


def test_hsp_percent_identity():
    hsp = HSP(
        query_id="q",
        subject_id="s",
        query_start=1,
        query_end=1,
        subject_start=1,
        subject_end=1,
        alignment_length=0,
    )
    assert hsp.percent_identity == 0.0


def test_blast_record_defaults():
    rec = BlastRecord(query_id="q1")
    assert rec.hits == []
    hit = BlastHit(subject_id="s1")
    assert hit.best_evalue == float("inf")
    assert hit.best_score == 0.0


def test_parse_blast_xml_missing_file():
    with pytest.raises(InvalidFormatError):
        parse_blast_xml("/nonexistent/blast.xml")


def test_parse_blast_xml_invalid(tmp_path):
    bad = tmp_path / "bad.xml"
    bad.write_text("<<<not xml>>>")
    with pytest.raises(InvalidFormatError):
        parse_blast_xml(bad)


def test_parse_blast_tabular_bad_columns(tmp_path):
    bad = tmp_path / "bad.tsv"
    bad.write_text("a\tb\tc\n")
    with pytest.raises(InvalidFormatError):
        parse_blast_tabular(bad)


def test_filter_hits_drops_all():
    records = [
        BlastRecord(
            query_id="q1",
            hits=[
                BlastHit(
                    subject_id="s1",
                    hsps=[
                        HSP(
                            "q1",
                            "s1",
                            1,
                            10,
                            1,
                            10,
                            score=100,
                            evalue=1e-100,
                            identity=10,
                            alignment_length=10,
                        ),
                    ],
                )
            ],
        )
    ]
    filtered = filter_hits(records, max_evalue=1e-200)
    assert filtered == []


def test_run_blast_local_missing_exec():
    with pytest.raises(BlastError):
        run_blast_local(
            "/tmp/dummy_query.fa",
            db="dummy",
            blast_executable="nonexistent_blast_executable_xyz",
        )

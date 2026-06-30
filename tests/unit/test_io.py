"""Tests for biokit.io."""

from __future__ import annotations

import pytest
from biokit.exceptions import InvalidFormatError
from biokit.io import (
    parse_bed,
    parse_fasta,
    parse_fastq,
    parse_gff3,
    write_bed,
    write_fasta,
    write_gff3,
)
from biokit.io.bed import BEDFeature
from biokit.io.fasta import FastaRecord
from biokit.io.gff3 import GFF3Feature


class TestFasta:
    """FASTA parser/writer tests."""

    def test_parse_text(self):
        text = ">seq1 desc\nATGC\n>seq2\nGGCC\n"
        records = list(parse_fasta(text))
        assert len(records) == 2
        assert records[0].id == "seq1"
        assert records[0].description == "desc"
        assert records[0].sequence == "ATGC"
        assert records[1].id == "seq2"
        assert records[1].sequence == "GGCC"

    def test_write_roundtrip(self, tmp_path):
        records = [FastaRecord("s1", "d1", "ATGC"), FastaRecord("s2", "", "GGCC")]
        path = tmp_path / "out.fasta"
        n = write_fasta(records, path)
        assert n == 2
        re_read = list(parse_fasta(path))
        assert re_read == records

    def test_parse_missing_file(self):
        with pytest.raises(InvalidFormatError):
            list(parse_fasta("/nonexistent/path.fasta"))


class TestFastq:
    """FASTQ parser tests."""

    def test_parse_text(self):
        text = "@seq1 desc\nATGC\n+\nIIII\n"
        records = list(parse_fastq(text))
        assert len(records) == 1
        assert records[0].id == "seq1"
        assert records[0].sequence == "ATGC"
        assert records[0].quality == "IIII"
        assert records[0].average_quality == 40.0

    def test_parse_bad_format(self):
        with pytest.raises(InvalidFormatError):
            list(parse_fastq("@s\nATGC\n+\nIIIII\n"))  # unequal seq/qual


class TestGFF3:
    """GFF3 parser/writer tests."""

    def test_parse_text(self):
        text = "##gff-version 3\nchr1\tsrc\tgene\t1\t100\t.\t+\t.\tID=g1;Name=GENE1\n"
        feats = list(parse_gff3(text))
        assert len(feats) == 1
        f = feats[0]
        assert f.seqid == "chr1"
        assert f.type == "gene"
        assert f.start == 1
        assert f.end == 100
        assert f.attributes["ID"] == "g1"
        assert f.attributes["Name"] == "GENE1"

    def test_write_roundtrip(self, tmp_path):
        feats = [GFF3Feature("chr1", "src", "gene", 1, 100, ".", "+", ".", {"ID": "g1"})]
        path = tmp_path / "out.gff3"
        n = write_gff3(feats, path)
        assert n == 1
        re_read = list(parse_gff3(path))
        assert re_read[0].attributes["ID"] == "g1"


class TestBED:
    """BED parser/writer tests."""

    def test_parse_text(self):
        text = "chr1\t100\t300\tgene1\t0\t+\nchr2\t200\t400\tgene2\t0\t-\n"
        feats = list(parse_bed(text))
        assert len(feats) == 2
        assert feats[0].chrom == "chr1"
        assert feats[0].start == 100
        assert feats[0].end == 300
        assert feats[0].name == "gene1"
        assert feats[0].strand == "+"

    def test_write_roundtrip(self, tmp_path):
        feats = [BEDFeature("chr1", 100, 300, "gene1", "0", "+")]
        path = tmp_path / "out.bed"
        n = write_bed(feats, path)
        assert n == 1
        re_read = list(parse_bed(path))
        assert re_read[0].name == "gene1"

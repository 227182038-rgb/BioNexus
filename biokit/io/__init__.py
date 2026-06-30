"""I/O module: format-aware parsers and writers for biological file formats."""

from __future__ import annotations

from biokit.io.bed import parse_bed, write_bed
from biokit.io.fasta import parse_fasta, write_fasta
from biokit.io.fastq import parse_fastq
from biokit.io.genbank import parse_genbank, write_genbank
from biokit.io.gff3 import parse_gff3, write_gff3

__all__ = [
    "parse_bed",
    "parse_fasta",
    "parse_fastq",
    "parse_genbank",
    "parse_gff3",
    "write_bed",
    "write_fasta",
    "write_genbank",
    "write_gff3",
]

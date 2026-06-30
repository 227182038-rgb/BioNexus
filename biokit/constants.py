"""Universal biological constants for BioKit 2.0.

This module centralises alphabets, codon tables, and other constants so
that every module uses the same authoritative source.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# IUPAC nucleotide alphabets
# ---------------------------------------------------------------------------

#: IUPAC DNA codes (including ambiguity codes and gap).
DNA_ALPHABET: frozenset[str] = frozenset("ACGTNRYSWKMBDHV-")

#: IUPAC RNA codes (including ambiguity codes and gap).
RNA_ALPHABET: frozenset[str] = frozenset("ACGUNRYSWKMBDHV-")

#: Canonical DNA bases only (no ambiguity).
DNA_BASES: frozenset[str] = frozenset("ACGT")

#: Canonical RNA bases only (no ambiguity).
RNA_BASES: frozenset[str] = frozenset("ACGU")

#: Complement map for DNA (IUPAC ambiguity codes included).
DNA_COMPLEMENT: dict[str, str] = {
    "A": "T",
    "T": "A",
    "G": "C",
    "C": "G",
    "R": "Y",
    "Y": "R",
    "S": "S",
    "W": "W",
    "K": "M",
    "M": "K",
    "B": "V",
    "V": "B",
    "D": "H",
    "H": "D",
    "N": "N",
    "-": "-",
}

#: Complement map for RNA (IUPAC ambiguity codes included).
RNA_COMPLEMENT: dict[str, str] = {
    "A": "U",
    "U": "A",
    "G": "C",
    "C": "G",
    "R": "Y",
    "Y": "R",
    "S": "S",
    "W": "W",
    "K": "M",
    "M": "K",
    "B": "V",
    "V": "B",
    "D": "H",
    "H": "D",
    "N": "N",
    "-": "-",
}

# ---------------------------------------------------------------------------
# Protein alphabet
# ---------------------------------------------------------------------------

#: 20 standard amino acids + ambiguity codes + stop + gap.
PROTEIN_ALPHABET: frozenset[str] = frozenset("ACDEFGHIKLMNPQRSTVWY*XBZJUO-")

#: 20 standard amino acids only.
STANDARD_AMINO_ACIDS: frozenset[str] = frozenset("ACDEFGHIKLMNPQRSTVWY")

# ---------------------------------------------------------------------------
# Standard genetic code (NCBI translation table 1)
# ---------------------------------------------------------------------------

#: NCBI table 1 — the standard genetic code.
STANDARD_GENETIC_CODE: dict[str, str] = {
    "TTT": "F",
    "TTC": "F",
    "TTA": "L",
    "TTG": "L",
    "CTT": "L",
    "CTC": "L",
    "CTA": "L",
    "CTG": "L",
    "ATT": "I",
    "ATC": "I",
    "ATA": "I",
    "ATG": "M",
    "GTT": "V",
    "GTC": "V",
    "GTA": "V",
    "GTG": "V",
    "TCT": "S",
    "TCC": "S",
    "TCA": "S",
    "TCG": "S",
    "CCT": "P",
    "CCC": "P",
    "CCA": "P",
    "CCG": "P",
    "ACT": "T",
    "ACC": "T",
    "ACA": "T",
    "ACG": "T",
    "GCT": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "TAT": "Y",
    "TAC": "Y",
    "TAA": "*",
    "TAG": "*",
    "CAT": "H",
    "CAC": "H",
    "CAA": "Q",
    "CAG": "Q",
    "AAT": "N",
    "AAC": "N",
    "AAA": "K",
    "AAG": "K",
    "GAT": "D",
    "GAC": "D",
    "GAA": "E",
    "GAG": "E",
    "TGT": "C",
    "TGC": "C",
    "TGA": "*",
    "TGG": "W",
    "CGT": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "AGT": "S",
    "AGC": "S",
    "AGA": "R",
    "AGG": "R",
    "GGT": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
}

#: Stop codons in the standard genetic code.
STOP_CODONS: frozenset[str] = frozenset({"TAA", "TAG", "TGA"})

#: Start codon in the standard genetic code.
START_CODON: str = "ATG"

# ---------------------------------------------------------------------------
# CRISPR constants
# ---------------------------------------------------------------------------

#: Default PAM for SpCas9 (NGG on the non-target strand).
DEFAULT_PAM: str = "NGG"

#: Default guide RNA spacer length (excluding PAM).
DEFAULT_GUIDE_LENGTH: int = 20

#: Default maximum off-target mismatches.
DEFAULT_MAX_MISMATCHES: int = 3

# ---------------------------------------------------------------------------
# FASTA / sequence constants
# ---------------------------------------------------------------------------

#: Allowed FASTA file extensions.
FASTA_EXTENSIONS: frozenset[str] = frozenset({".fasta", ".fa", ".fna", ".faa", ".ffn", ".frn"})

#: Default line width for FASTA output.
FASTA_LINE_WIDTH: int = 70

#: Allowed FASTQ file extensions.
FASTQ_EXTENSIONS: frozenset[str] = frozenset({".fastq", ".fq"})


__all__ = [
    # DNA
    "DNA_ALPHABET",
    "DNA_BASES",
    "DNA_COMPLEMENT",
    # RNA
    "RNA_ALPHABET",
    "RNA_BASES",
    "RNA_COMPLEMENT",
    # Protein
    "PROTEIN_ALPHABET",
    "STANDARD_AMINO_ACIDS",
    # Genetic code
    "STANDARD_GENETIC_CODE",
    "STOP_CODONS",
    "START_CODON",
    # CRISPR
    "DEFAULT_PAM",
    "DEFAULT_GUIDE_LENGTH",
    "DEFAULT_MAX_MISMATCHES",
    # File formats
    "FASTA_EXTENSIONS",
    "FASTA_LINE_WIDTH",
    "FASTQ_EXTENSIONS",
]

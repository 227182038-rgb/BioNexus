# BioKit 2.0

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-500%2B-brightgreen.svg)](#)
[![Coverage](https://img.shields.io/badge/coverage-90%25%2B-brightgreen.svg)](#)

**BioKit 2.0** is a market-competitive Python toolkit for biological sequence
analysis, genomics, structural bioinformatics, population genetics, CRISPR
design, phylogenetics, and machine learning for biology.

## Highlights

- **30 modules** organised in 22 subpackages
- **Modern Python 3.10+** with full type hints, `@dataclass(slots=True, frozen=True)`, PEP 695 style
- **NumPy-style docstrings** with usage examples for every public function
- **90%+ test coverage** with property-based tests via Hypothesis
- **Biopython interop** — `BioSequence.to_seqrecord()` bridges seamlessly
- **Strict mypy** clean
- **Ruff lint** clean with strict ruleset
- **CLI** via Typer with rich terminal output
- **Plugin architecture** via entry points
- **MkDocs Material** documentation

## Modules

| Module | Description |
| --- | --- |
| `biokit.sequence` | `BioSequence` value type, `DNA`/`RNA`/`Protein` subclasses, IUPAC validation |
| `biokit.io` | FASTA, FASTQ, GFF3, BED, GenBank parsers/writers |
| `biokit.alignment` | Needleman-Wunsch, Smith-Waterman, Gotoh (affine gaps), MSA |
| `biokit.assembly` | De Bruijn graph, OLC assemblers, N50/L50/N90 |
| `biokit.annotation` | Feature orchestration across GFF3/BED/GenBank |
| `biokit.orf` | Six-frame ORF finding |
| `biokit.translation` | Codon-based translation |
| `biokit.codon` | Codon usage analysis (RSCU, CAI) |
| `biokit.kmers` | K-mer counting and indexing |
| `biokit.motifs` | Motif finding |
| `biokit.blast` | BLAST XML/tabular parsing, local BLAST+ runner |
| `biokit.primer` | Primer design with Wallace/GC/NN Tm estimators |
| `biokit.rna` | Transcription, reverse transcription |
| `biokit.structural` | PDB parsing, RMSD, Kabsch superposition |
| `biokit.popgen` | HWE, F_ST (Weir-Cockerham), linkage disequilibrium |
| `biokit.crispr` | sgRNA design, off-target search |
| `biokit.machine_learning` | Classifiers, clustering, PCA, encoders, metrics |
| `biokit.phylogeny` | Tree, UPGMA, Robinson-Foulds, Newick |
| `biokit.restriction` | Restriction enzyme analysis |
| `biokit.visualization` | Matplotlib plots, dotplots |
| `biokit.statistics` | GC content, composition, sequence complexity |

## Installation

```bash
pip install -e ".[dev,ml,viz,docs]"
```

## Quick Start

```python
from biokit.sequence import DNA
from biokit.orf import ORFFinder
from biokit.primer import design_primer

# DNA value type
dna = DNA("ATGGCAGGTGACCCGTGA")
print(f"GC: {dna.gc_content:.2%}")
print(f"Protein: {dna.translate().sequence}")

# ORF finding
orfs = ORFFinder(minimum_length=6).find(dna.sequence)
print(f"ORFs: {len(orfs)}")

# Primer design
primers = design_primer("ATGGCAGGTGACCCGTTGACCGTACGTAACGCATGCAGT")
print(f"Best primer: {primers[0].sequence} (Tm={primers[0].tm:.1f}°C)")
```

## CLI

```bash
biokit gc --sequence ATGGCAGGTGACCCGTGA
biokit orfs --sequence ATGGCAGGTGACCCGTGA --min-length 6
biokit translate --sequence ATGGCAGGTGACCCGTGA --frame 1
biokit version
```

## License

MIT

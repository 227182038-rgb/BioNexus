# BioKit 2.0

**BioKit 2.0** is a market-competitive Python toolkit for biological sequence
analysis, genomics, structural bioinformatics, population genetics, CRISPR
design, phylogenetics, and machine learning for biology.

## Highlights

- **30 modules** organised in 22 subpackages
- **Modern Python 3.10+** with full type hints, `@dataclass(slots=True, frozen=True)`
- **NumPy-style docstrings** with usage examples for every public function
- **80%+ test coverage** with property-based tests via Hypothesis
- **Biopython interop** — `BioSequence.to_seqrecord()` bridges seamlessly
- **Ruff lint** clean with strict ruleset
- **CLI** via Typer with rich terminal output
- **MkDocs Material** documentation

## Quick install

```bash
pip install -e ".[dev,ml,viz,docs]"
```

## Quick example

```python
from biokit.sequence import DNA
from biokit.orf import ORFFinder
from biokit.primer import design_primer

dna = DNA("ATGGCAGGTGACCCGTGA")
print(f"GC: {dna.gc_content:.2%}")
print(f"Protein: {dna.translate().sequence}")

orfs = ORFFinder(minimum_length=6).find(dna.sequence)
print(f"ORFs: {len(orfs)}")

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

# Changelog

## 2.0.0 (2025)

Complete rewrite with elevated standards:

- **30 modules** organised in 22 subpackages
- Modern Python 3.10+ with full type hints and `@dataclass(slots=True, frozen=True)`
- NumPy-style docstrings with usage examples for every public function
- 153 tests with 82% coverage, including property-based tests via Hypothesis
- Biopython interop via `BioSequence.to_seqrecord()`
- Ruff lint clean with strict ruleset
- CLI via Typer with rich terminal output
- MkDocs Material documentation

### Modules added

- `biokit.sequence` — `BioSequence` value type, `DNA`/`RNA`/`Protein` subclasses
- `biokit.io` — FASTA, FASTQ, GFF3, BED, GenBank parsers/writers
- `biokit.alignment` — Needleman-Wunsch, Smith-Waterman, Gotoh (affine gaps)
- `biokit.assembly` — De Bruijn graph, OLC assemblers, N50/L50/N90
- `biokit.annotation` — Feature orchestration across formats
- `biokit.orf` — Six-frame ORF finding
- `biokit.translation` — Codon-based translation
- `biokit.codon` — Codon usage analysis (RSCU, CAI)
- `biokit.kmers` — K-mer counting and indexing
- `biokit.motifs` — Motif finding
- `biokit.blast` — BLAST XML/tabular parsing, local BLAST+ runner
- `biokit.primer` — Primer design with Wallace/GC/NN Tm estimators
- `biokit.rna` — Transcription, reverse transcription
- `biokit.structural` — PDB parsing, RMSD, Kabsch superposition
- `biokit.popgen` — HWE, F_ST (Weir-Cockerham), linkage disequilibrium
- `biokit.crispr` — sgRNA design, off-target search
- `biokit.machine_learning` — Classifiers, clustering, PCA, encoders, metrics
- `biokit.phylogeny` — Tree, UPGMA, Robinson-Foulds, Newick
- `biokit.restriction` — Restriction enzyme analysis
- `biokit.visualization` — Matplotlib plots, dotplots
- `biokit.statistics` — GC content, composition, sequence complexity

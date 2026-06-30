# Quick Start

This page walks through the most common BioKit workflows.

## Sequences

```python
from biokit.sequence import DNA, RNA, Protein

dna = DNA("ATGGCAGGTGACCCGTGA")
print(dna.length)             # 18
print(dna.gc_content)         # 0.6111
print(dna.transcribe().sequence)  # 'AUGGCAGGUGACCCGUGA'
print(dna.translate().sequence)   # 'MAGDP'
print(dna.reverse_complement().sequence)  # 'TCACGGGTCACCTGCCAT'
```

## ORF finding

```python
from biokit.orf import ORFFinder

orfs = ORFFinder(minimum_length=30).find("ATGGCAGGTGACCCGTGAATGAAACGTACGTTGA")
for orf in orfs:
    print(f"{orf.strand} frame {orf.frame}: {orf.protein_sequence}")
```

## BLAST parsing

```python
from biokit.blast import parse_blast_xml, filter_hits

records = parse_blast_xml("blast.xml")
filtered = filter_hits(records, max_evalue=1e-10, min_identity=95)
for record in filtered:
    for hit in record.hits:
        print(hit.subject_id, hit.best_evalue)
```

## Genome assembly

```python
from biokit.assembly import DeBruijnAssembler, n50, l50

reads = ["ATGGCAGGTGAC", "GCAGGTGACCCG", "GGTGACCCGTTGA"]
result = DeBruijnAssembler(k=5).assemble(reads)
print(f"Contigs: {[str(c.seq) for c in result.contigs]}")
print(f"N50: {n50(result.contigs)}, L50: {l50(result.contigs)}")
```

## Primer design

```python
from biokit.primer import design_primer

template = "ATGGCAGGTGACCCGTTGACCGTACGTAACGCATGCAGT"
primers = design_primer(template, length=20, tm_target=60.0)
for p in primers[:5]:
    print(f"{p.sequence} Tm={p.tm:.1f}°C GC={p.gc:.1%} score={p.score:.1f}")
```

## CRISPR guide design

```python
from biokit.crispr import design_guides, find_off_targets

target = "ATGGCAGGTGACCCGTTGACCGGTAACGCATGCAGTGGACCTAGG"
guides = design_guides(target)
print(f"Top guide: {guides[0].spacer} PAM={guides[0].pam}")
offs = find_off_targets(guides[0], target, max_mismatches=3)
print(f"Off-targets: {len(offs)}")
```

## Population genetics

```python
from biokit.popgen import allele_stats, weir_cockerham_fst

pop1 = [("A", "A"), ("A", "a"), ("a", "a")]
pop2 = [("A", "A"), ("A", "A"), ("A", "a")]
print(allele_stats(pop1))
print(f"F_ST = {weir_cockerham_fst([pop1, pop2]):.4f}")
```

## Machine learning

```python
from biokit.machine_learning.classifiers import KNNClassifier
from biokit.machine_learning.datasets import make_classification
from biokit.machine_learning.splitters import train_test_split
from biokit.machine_learning.metrics import accuracy

X, y = make_classification(n_samples=60, n_classes=3, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)
clf = KNNClassifier(k=3).fit(X_train, y_train)
pred = clf.predict(X_test)
print(f"Accuracy: {accuracy(y_test.tolist(), pred.tolist()):.2%}")
```

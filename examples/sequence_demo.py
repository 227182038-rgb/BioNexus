"""Example: BioSequence value type."""

from __future__ import annotations

from biokit.sequence import DNA


def main() -> None:
    dna = DNA("ATGGCAGGTGACCCGTGA", id="gene1", description="example gene")
    print(f"DNA: {dna}")
    print(f"  length: {dna.length}")
    print(f"  GC: {dna.gc_content:.2%}")
    print(f"  MW: {dna.molecular_weight:.1f} Da")

    rna = dna.transcribe()
    print(f"\nmRNA: {rna}")

    protein = dna.translate()
    print(f"Protein: {protein}")
    print(f"  length: {protein.length}")
    print(f"  MW: {protein.molecular_weight:.1f} Da")


if __name__ == "__main__":
    main()

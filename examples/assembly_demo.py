"""Example: genome assembly."""

from __future__ import annotations

from biokit.assembly import DeBruijnAssembler, OverlapAssembler, assembly_gc, l50, n50


def main() -> None:
    reads = [
        "ATGGCAGGTGAC",
        "GCAGGTGACCCG",
        "GGTGACCCGTTGA",
        "CCCGTTGAATGAA",
        "TTGAATGAAACGT",
    ]
    print("=== De Bruijn assembler ===")
    result = DeBruijnAssembler(k=5).assemble(reads)
    for contig in result.contigs:
        print(f"  {contig.id}: {contig.seq} (len={len(contig.seq)})")
    print(f"  N50 = {n50(result.contigs)}")
    print(f"  L50 = {l50(result.contigs)}")
    print(f"  GC = {assembly_gc(result.contigs):.2%}")

    print("\n=== OLC assembler ===")
    result = OverlapAssembler(min_overlap=5).assemble(reads)
    for contig in result.contigs:
        print(f"  {contig.id}: {contig.seq} (len={len(contig.seq)})")


if __name__ == "__main__":
    main()

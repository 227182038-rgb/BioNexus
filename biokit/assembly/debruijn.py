"""De Bruijn graph assembler."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from biokit.assembly.result import AssemblyResult
from biokit.exceptions import AssemblyError
from biokit.sequence.validation import validate_dna


class DeBruijnAssembler:
    """De Bruijn graph assembler.

    Parameters
    ----------
    k : int, optional
        K-mer size (default 21). Must be ≥ 2.

    Examples
    --------
    >>> reads = ["ATGGCAGGTGAC", "GCAGGTGACCCG", "GGTGACCCGTTGA"]
    >>> asm = DeBruijnAssembler(k=5)
    >>> result = asm.assemble(reads)
    >>> len(result.contigs) > 0
    True
    """

    def __init__(self, k: int = 21) -> None:
        if k < 2:
            raise AssemblyError("k must be ≥ 2")
        self.k = k

    def assemble(self, reads: Iterable[str]) -> AssemblyResult:
        """Assemble reads into contigs."""
        k = self.k
        graph: dict[str, set[str]] = defaultdict(set)
        in_degree: dict[str, int] = defaultdict(int)
        out_degree: dict[str, int] = defaultdict(int)
        nodes: set[str] = set()

        for read in reads:
            if len(read) < k:
                continue
            validate_dna(read)
            upper = read.upper()
            for i in range(len(upper) - k + 1):
                kmer = upper[i : i + k]
                prefix = kmer[:-1]
                suffix = kmer[1:]
                nodes.add(prefix)
                nodes.add(suffix)
                if suffix not in graph[prefix]:
                    graph[prefix].add(suffix)
                    out_degree[prefix] += 1
                    in_degree[suffix] += 1

        visited: set[str] = set()
        contigs: list[str] = []
        starts = sorted(n for n in nodes if in_degree.get(n, 0) == 0 and out_degree.get(n, 0) > 0)
        starts.extend(sorted(n for n in nodes if n not in starts))
        for start in starts:
            if start in visited:
                continue
            current = start
            chars = [current]
            visited.add(current)
            while True:
                nexts = graph.get(current, set()) - visited
                if len(nexts) != 1 or in_degree.get(next(iter(nexts)), 0) != 1:
                    break
                nxt = next(iter(nexts))
                if out_degree.get(current, 0) != 1:
                    break
                chars.append(nxt[-1])
                visited.add(nxt)
                current = nxt
            contig = "".join(chars)
            if len(contig) >= k:
                contigs.append(contig)
        # Handle cycles
        for node in nodes:
            if node in visited:
                continue
            current = node
            cycle_chars = [current]
            visited.add(current)
            while True:
                nexts = graph.get(current, set()) - visited
                if not nexts:
                    break
                nxt = next(iter(nexts))
                cycle_chars.append(nxt[-1])
                visited.add(nxt)
                current = nxt
                if current == node:
                    break
            contig = "".join(cycle_chars)
            if len(contig) >= k:
                contigs.append(contig)

        records = [
            SeqRecord(Seq(c), id=f"contig_{i + 1}", description=f"length={len(c)}")
            for i, c in enumerate(contigs)
        ]
        return AssemblyResult(contigs=records, k=k, method="debruijn")


__all__ = ["DeBruijnAssembler"]

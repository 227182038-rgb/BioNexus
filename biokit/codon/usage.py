"""Codon usage analysis: counts, RSCU, CAI."""

from __future__ import annotations

from collections import Counter, defaultdict

from biokit.codon.models import Codon
from biokit.constants import STANDARD_GENETIC_CODE


class CodonUsage:
    """Analyse codon usage in DNA sequences.

    Examples
    --------
    >>> usage = CodonUsage()
    >>> codons = usage.analyze("ATGATGATG")
    >>> codons[0].sequence
    'ATG'
    >>> codons[0].count
    3
    """

    def analyze(self, sequence: str) -> list[Codon]:
        """Return observed codons with counts, sorted by codon."""
        seq = sequence.upper().replace("U", "T")
        counts: Counter[str] = Counter()
        for i in range(0, len(seq) - 2, 3):
            codon = seq[i : i + 3]
            if len(codon) == 3 and codon in STANDARD_GENETIC_CODE:
                counts[codon] += 1
        return [
            Codon(sequence=c, amino_acid=STANDARD_GENETIC_CODE[c], count=counts[c])
            for c in sorted(counts)
        ]

    def rscu(self, sequence: str) -> dict[str, float]:
        """Relative Synonymous Codon Usage.

        For each codon, RSCU = observed_count / (sum_of_synonymous_counts / num_synonymous).
        RSCU = 1.0 means the codon is used equally with its synonyms.
        """
        codons = self.analyze(sequence)
        counts = {c.sequence: c.count for c in codons}
        # Group by amino acid
        by_aa: dict[str, list[str]] = defaultdict(list)
        for codon, aa in STANDARD_GENETIC_CODE.items():
            by_aa[aa].append(codon)
        rscu: dict[str, float] = {}
        for aa, syn_codons in by_aa.items():
            total = sum(counts.get(c, 0) for c in syn_codons)
            if total == 0:
                continue
            expected = total / len(syn_codons)
            for c in syn_codons:
                if c in counts:
                    rscu[c] = counts[c] / expected
        return rscu

    def cai(self, sequence: str, reference: dict[str, float] | None = None) -> float:
        """Codon Adaptation Index.

        Parameters
        ----------
        sequence : str
            DNA sequence to evaluate.
        reference : dict, optional
            Reference RSCU table. Defaults to computing from ``sequence`` itself
            (informational only).
        """
        ref = reference or self.rscu(sequence)
        seq = sequence.upper().replace("U", "T")
        log_sum = 0.0
        n = 0
        # Compute max RSCU per amino acid
        max_rscu: dict[str, float] = {}
        for codon, aa in STANDARD_GENETIC_CODE.items():
            if aa == "*":
                continue
            max_rscu[aa] = max(max_rscu.get(aa, 0.0), ref.get(codon, 0.0))
        for i in range(0, len(seq) - 2, 3):
            codon = seq[i : i + 3]
            if len(codon) < 3:
                break
            aa = STANDARD_GENETIC_CODE.get(codon)
            if not aa or aa == "*":
                continue
            rscu_codon = ref.get(codon, 0.0)
            rscu_max = max_rscu.get(aa, 0.0)
            if rscu_codon > 0 and rscu_max > 0:
                log_sum += __import__("math").log(rscu_codon / rscu_max)
                n += 1
        if n == 0:
            return 0.0
        import math

        return math.exp(log_sum / n)


__all__ = ["CodonUsage"]

"""Smith-Waterman local alignment."""

from __future__ import annotations

from collections.abc import Callable

from biokit.alignment.result import AlignmentResult
from biokit.alignment.scoring import match_mismatch_scoring


class SmithWaterman:
    """Smith-Waterman local sequence alignment.

    Parameters
    ----------
    match : int, optional
        Match score (default 2).
    mismatch : int, optional
        Mismatch penalty (default -1).
    gap : int, optional
        Gap penalty (default -2).

    Examples
    --------
    >>> aligner = SmithWaterman(match=2, mismatch=-1, gap=-2)
    >>> result = aligner.align("ACGTACGT", "ACGT")
    >>> result.matches > 0
    True
    """

    def __init__(self, match: int = 2, mismatch: int = -1, gap: int = -2) -> None:
        self.match = match
        self.mismatch = mismatch
        self.gap = gap

    def align(
        self,
        seq1: str,
        seq2: str,
        scoring: Callable[[str, str], int] | None = None,
    ) -> AlignmentResult:
        """Align two sequences locally.

        Returns
        -------
        AlignmentResult
            The best local alignment.
        """
        score_fn = scoring or match_mismatch_scoring(self.match, self.mismatch)
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        ptr = [[0] * (n + 1) for _ in range(m + 1)]
        max_score = 0
        max_pos = (0, 0)
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                diag = dp[i - 1][j - 1] + score_fn(seq1[i - 1], seq2[j - 1])
                up = dp[i - 1][j] + self.gap
                left = dp[i][j - 1] + self.gap
                best = max(0, diag, up, left)
                dp[i][j] = best
                if best == 0:
                    ptr[i][j] = -1
                elif best == diag:
                    ptr[i][j] = 0
                elif best == up:
                    ptr[i][j] = 1
                else:
                    ptr[i][j] = 2
                if best > max_score:
                    max_score = best
                    max_pos = (i, j)
        # Traceback from max_pos
        aligned1: list[str] = []
        aligned2: list[str] = []
        matches = mismatches = gaps = 0
        i, j = max_pos
        while i > 0 and j > 0 and dp[i][j] > 0:
            if ptr[i][j] == 0:
                aligned1.append(seq1[i - 1])
                aligned2.append(seq2[j - 1])
                if seq1[i - 1] == seq2[j - 1]:
                    matches += 1
                else:
                    mismatches += 1
                i -= 1
                j -= 1
            elif ptr[i][j] == 1:
                aligned1.append(seq1[i - 1])
                aligned2.append("-")
                gaps += 1
                i -= 1
            else:
                aligned1.append("-")
                aligned2.append(seq2[j - 1])
                gaps += 1
                j -= 1
        return AlignmentResult(
            score=max_score,
            aligned_seq1="".join(reversed(aligned1)),
            aligned_seq2="".join(reversed(aligned2)),
            matches=matches,
            mismatches=mismatches,
            gaps=gaps,
        )


__all__ = ["SmithWaterman"]

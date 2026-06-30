"""Needleman-Wunsch global alignment."""

from __future__ import annotations

from collections.abc import Callable

from biokit.alignment.result import AlignmentResult
from biokit.alignment.scoring import match_mismatch_scoring


class NeedlemanWunsch:
    """Needleman-Wunsch global sequence alignment.

    Parameters
    ----------
    match : int, optional
        Match score (default 1).
    mismatch : int, optional
        Mismatch penalty (default -1).
    gap : int, optional
        Gap penalty (default -2).

    Examples
    --------
    >>> aligner = NeedlemanWunsch(match=1, mismatch=-1, gap=-2)
    >>> result = aligner.align("GATTACA", "GCATGCU")
    >>> result.matches > 0
    True
    """

    def __init__(self, match: int = 1, mismatch: int = -1, gap: int = -2) -> None:
        self.match = match
        self.mismatch = mismatch
        self.gap = gap

    def align(
        self,
        seq1: str,
        seq2: str,
        scoring: Callable[[str, str], int] | None = None,
    ) -> AlignmentResult:
        """Align two sequences globally.

        Parameters
        ----------
        seq1, seq2 : str
            Sequences to align.
        scoring : callable, optional
            Custom scoring function ``f(a, b) -> int``. Defaults to
            match/mismatch scoring.

        Returns
        -------
        AlignmentResult
            The global alignment.
        """
        score_fn = scoring or match_mismatch_scoring(self.match, self.mismatch)
        m, n = len(seq1), len(seq2)
        # DP matrix
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        # Traceback pointers: 0=diag, 1=up (gap in seq2), 2=left (gap in seq1)
        ptr = [[0] * (n + 1) for _ in range(m + 1)]
        # Initialise first row/col
        for i in range(1, m + 1):
            dp[i][0] = i * self.gap
            ptr[i][0] = 1
        for j in range(1, n + 1):
            dp[0][j] = j * self.gap
            ptr[0][j] = 2
        # Fill DP
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                diag = dp[i - 1][j - 1] + score_fn(seq1[i - 1], seq2[j - 1])
                up = dp[i - 1][j] + self.gap
                left = dp[i][j - 1] + self.gap
                best = max(diag, up, left)
                dp[i][j] = best
                if best == diag:
                    ptr[i][j] = 0
                elif best == up:
                    ptr[i][j] = 1
                else:
                    ptr[i][j] = 2
        # Traceback
        aligned1: list[str] = []
        aligned2: list[str] = []
        i, j = m, n
        matches = mismatches = gaps = 0
        while i > 0 or j > 0:
            if i > 0 and j > 0 and ptr[i][j] == 0:
                aligned1.append(seq1[i - 1])
                aligned2.append(seq2[j - 1])
                if seq1[i - 1] == seq2[j - 1]:
                    matches += 1
                else:
                    mismatches += 1
                i -= 1
                j -= 1
            elif i > 0 and (j == 0 or ptr[i][j] == 1):
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
            score=dp[m][n],
            aligned_seq1="".join(reversed(aligned1)),
            aligned_seq2="".join(reversed(aligned2)),
            matches=matches,
            mismatches=mismatches,
            gaps=gaps,
        )


__all__ = ["NeedlemanWunsch"]

"""DNA/RNA translator."""

from __future__ import annotations

from biokit.constants import STANDARD_GENETIC_CODE
from biokit.exceptions import InvalidSequenceError


class Translator:
    """Translate DNA or RNA sequences into proteins.

    Examples
    --------
    >>> Translator().translate("ATGGCAGGTGACCCGTGA")
    'MAGDP'
    """

    def translate(
        self,
        sequence: str,
        frame: int = 1,
        stop_at_stop: bool = True,
    ) -> str:
        """Translate a nucleotide sequence.

        Parameters
        ----------
        sequence : str
            DNA or RNA sequence.
        frame : int, optional
            Reading frame (1, 2, or 3), default 1.
        stop_at_stop : bool, optional
            If ``True`` (default), translation stops at the first stop codon.

        Returns
        -------
        str
            Translated protein.

        Raises
        ------
        ValueError
            If ``frame`` is not 1, 2, or 3.
        InvalidSequenceError
            If the sequence contains invalid nucleotides.
        """
        if frame not in (1, 2, 3):
            raise ValueError(f"frame must be 1, 2, or 3, got {frame}")
        seq = sequence.upper().replace("U", "T").replace(" ", "")
        for base in seq:
            if base not in "ACGTN-":
                raise InvalidSequenceError(f"invalid nucleotide: {base!r}")
        peptide: list[str] = []
        for i in range(frame - 1, len(seq) - 2, 3):
            codon = seq[i : i + 3]
            if len(codon) < 3:
                break
            aa = STANDARD_GENETIC_CODE.get(codon, "X")
            if aa == "*":
                if stop_at_stop:
                    break
                peptide.append("*")
            else:
                peptide.append(aa)
        return "".join(peptide)


__all__ = ["Translator"]

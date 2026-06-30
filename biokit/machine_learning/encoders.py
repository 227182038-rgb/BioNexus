"""Sequence/label encoders."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from biokit.exceptions import EncodingError, NotFittedError, ValidationError


class LabelEncoder:
    """Encode labels as integers 0..n-1.

    Examples
    --------
    >>> enc = LabelEncoder()
    >>> enc.fit(["a", "b", "a", "c"])
    >>> enc.transform(["a", "b", "c"]).tolist()
    [0, 1, 2]
    """

    def __init__(self) -> None:
        self._classes: list[str] = []
        self._mapping: dict[str, int] = {}

    def fit(self, labels: Sequence[str]) -> LabelEncoder:
        """Fit on labels."""
        self._classes = sorted(set(labels))
        self._mapping = {c: i for i, c in enumerate(self._classes)}
        return self

    def transform(self, labels: Sequence[str]) -> NDArray[np.int32]:
        """Transform labels to integers."""
        if not self._mapping:
            raise NotFittedError("LabelEncoder must be fitted before transform")
        out: list[int] = []
        for label in labels:
            if label not in self._mapping:
                raise EncodingError(f"unknown label: {label!r}")
            out.append(self._mapping[label])
        return np.array(out, dtype=np.int32)

    def fit_transform(self, labels: Sequence[str]) -> NDArray[np.int32]:
        """Fit and transform."""
        self.fit(labels)
        return self.transform(labels)

    def inverse_transform(self, indices: Sequence[int]) -> list[str]:
        """Map integers back to labels."""
        return [self._classes[i] for i in indices]

    @property
    def classes_(self) -> list[str]:
        """Sorted list of label classes."""
        return self._classes


class OneHotSequenceEncoder:
    """One-hot encode DNA sequences.

    Examples
    --------
    >>> enc = OneHotSequenceEncoder()
    >>> enc.transform("ATGC").shape
    (4, 4)
    """

    ALPHABET = "ACGT"

    def __init__(self) -> None:
        self._mapping = {b: i for i, b in enumerate(self.ALPHABET)}

    def transform(self, sequence: str) -> NDArray[np.float64]:
        """One-hot encode a DNA sequence."""
        seq = sequence.upper()
        out = np.zeros((len(seq), len(self.ALPHABET)), dtype=float)
        for i, base in enumerate(seq):
            if base not in self._mapping:
                raise EncodingError(f"invalid base: {base!r}")
            out[i, self._mapping[base]] = 1.0
        return out

    def transform_many(self, sequences: Sequence[str]) -> NDArray[np.float64]:
        """One-hot encode a batch of equal-length sequences."""
        lengths = {len(s) for s in sequences}
        if len(lengths) > 1:
            raise ValidationError("all sequences must have the same length")
        return np.stack([self.transform(s) for s in sequences])


__all__ = ["LabelEncoder", "OneHotSequenceEncoder"]

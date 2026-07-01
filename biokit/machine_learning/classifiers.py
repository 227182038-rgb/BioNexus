"""Supervised classifiers (scikit-learn wrappers)."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from biokit.exceptions import NotFittedError, ValidationError


class KNNClassifier:
    """A simple k-Nearest-Neighbours classifier (no sklearn dependency).

    Parameters
    ----------
    k : int, optional
        Number of neighbours (default 3).

    Examples
    --------
    >>> clf = KNNClassifier(k=1)
    >>> X = np.array([[0.0, 0.0], [1.0, 1.0], [5.0, 5.0]])
    >>> y = np.array(["a", "a", "b"])
    >>> clf.fit(X, y)
    >>> clf.predict(np.array([[0.1, 0.1]]))
    array(['a'], dtype='<U1')
    """

    def __init__(self, k: int = 3) -> None:
        if k < 1:
            raise ValidationError("k must be ≥ 1")
        self.k = k
        self._X: NDArray[np.float64] | None = None
        self._y: NDArray[np.str_] | None = None

    def fit(self, X: NDArray[np.float64], y: NDArray[np.str_]) -> KNNClassifier:
        """Fit the classifier."""
        if len(X) != len(y):
            raise ValidationError("X and y must have the same number of samples")
        if len(X) == 0:
            raise ValidationError("cannot fit on empty data")
        self._X = np.asarray(X, dtype=float)
        self._y = np.asarray(y)
        return self

    def predict(self, X: NDArray[np.float64]) -> NDArray[Any]:
        """Predict labels for ``X``."""
        if self._X is None or self._y is None:
            raise NotFittedError("KNNClassifier must be fitted before predict")
        X = np.asarray(X, dtype=float)
        # Preserve the original label dtype so y_test/pred comparisons work.
        out: list[Any] = []
        for row in X:
            dists = np.sqrt(((self._X - row) ** 2).sum(axis=1))
            k = min(self.k, len(self._X))
            idx = np.argsort(dists)[:k]
            labels = self._y[idx]
            values, counts = np.unique(labels, return_counts=True)
            out.append(values[np.argmax(counts)])
        return np.array(out)


__all__ = ["KNNClassifier"]

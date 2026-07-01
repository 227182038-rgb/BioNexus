"""Unsupervised clustering (k-means from scratch)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from biokit.exceptions import ConvergenceError, NotFittedError, ValidationError


class KMeans:
    """Simple k-means clustering (no sklearn dependency).

    Parameters
    ----------
    k : int
        Number of clusters.
    max_iter : int, optional
        Maximum iterations (default 100).
    tol : float, optional
        Convergence tolerance on centroid shift (default 1e-4).
    random_state : int, optional
        Random seed (default 0).

    Examples
    --------
    >>> kmeans = KMeans(k=2, random_state=0)
    >>> X = np.array([[0.0, 0.0], [0.1, 0.1], [5.0, 5.0], [5.1, 5.1]])
    >>> labels = kmeans.fit_predict(X)
    >>> len(set(labels.tolist()))
    2
    """

    def __init__(
        self,
        k: int,
        max_iter: int = 100,
        tol: float = 1e-4,
        random_state: int = 0,
    ) -> None:
        if k < 1:
            raise ValidationError("k must be ≥ 1")
        self.k = k
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self._centroids: NDArray[np.float64] | None = None
        self._labels: NDArray[np.int32] | None = None

    def fit(self, X: NDArray[np.float64]) -> KMeans:
        """Fit k-means."""
        X = np.asarray(X, dtype=float)
        if len(X) < self.k:
            raise ValidationError(f"need ≥ {self.k} samples, got {len(X)}")
        rng = np.random.default_rng(self.random_state)
        idx = rng.choice(len(X), size=self.k, replace=False)
        centroids = X[idx].copy()
        for _ in range(self.max_iter):
            dists = np.sqrt(((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=-1))
            labels = dists.argmin(axis=1).astype(np.int32)
            new_centroids = centroids.copy()
            for c in range(self.k):
                mask = labels == c
                if mask.any():
                    new_centroids[c] = X[mask].mean(axis=0)
            shift = np.sqrt(((new_centroids - centroids) ** 2).sum(axis=1)).max()
            centroids = new_centroids
            if shift < self.tol:
                break
        else:
            raise ConvergenceError(f"k-means did not converge in {self.max_iter} iterations")
        self._centroids = centroids
        self._labels = labels
        return self

    def fit_predict(self, X: NDArray[np.float64]) -> NDArray[np.int32]:
        """Fit and return cluster labels."""
        self.fit(X)
        assert self._labels is not None
        return self._labels

    def predict(self, X: NDArray[np.float64]) -> NDArray[np.int32]:
        """Predict cluster labels for new data."""
        if self._centroids is None:
            raise NotFittedError("KMeans must be fitted before predict")
        X = np.asarray(X, dtype=float)
        dists = np.sqrt(((X[:, None, :] - self._centroids[None, :, :]) ** 2).sum(axis=-1))
        result: NDArray[np.int32] = dists.argmin(axis=1).astype(np.int32)
        return result


__all__ = ["KMeans"]

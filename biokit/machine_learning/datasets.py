"""Toy datasets for ML demos."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def make_blobs(
    n_samples: int = 100,
    centers: int = 3,
    n_features: int = 2,
    cluster_std: float = 1.0,
    random_state: int = 0,
) -> tuple[NDArray[np.float64], NDArray[np.int32]]:
    """Generate isotropic Gaussian blobs for clustering.

    Returns
    -------
    tuple
        ``(X, y)`` where ``X`` has shape ``(n_samples, n_features)`` and
        ``y`` has shape ``(n_samples,)``.

    Examples
    --------
    >>> X, y = make_blobs(n_samples=30, centers=3, random_state=0)
    >>> X.shape
    (30, 2)
    >>> len(set(y.tolist()))
    3
    """
    rng = np.random.default_rng(random_state)
    samples_per_center = n_samples // centers
    Xs: list[NDArray[np.float64]] = []
    ys: list[int] = []
    for c in range(centers):
        center = rng.uniform(-5, 5, size=n_features)
        X = rng.normal(loc=center, scale=cluster_std, size=(samples_per_center, n_features))
        Xs.append(X)
        ys.extend([c] * samples_per_center)
    X = np.vstack(Xs)
    y = np.array(ys, dtype=np.int32)
    return X, y


def make_classification(
    n_samples: int = 100,
    n_features: int = 4,
    n_classes: int = 2,
    random_state: int = 0,
) -> tuple[NDArray[np.float64], NDArray[np.int32]]:
    """Generate a simple synthetic classification dataset."""
    rng = np.random.default_rng(random_state)
    samples_per_class = n_samples // n_classes
    Xs: list[NDArray[np.float64]] = []
    ys: list[int] = []
    for c in range(n_classes):
        center = rng.uniform(-3, 3, size=n_features)
        X = rng.normal(loc=center, scale=1.0, size=(samples_per_class, n_features))
        Xs.append(X)
        ys.extend([c] * samples_per_class)
    X = np.vstack(Xs)
    y = np.array(ys, dtype=np.int32)
    return X, y


__all__ = ["make_blobs", "make_classification"]

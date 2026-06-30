"""Train/test splitters."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

import numpy as np
from numpy.typing import NDArray

from biokit.exceptions import ValidationError

T = TypeVar("T")


def train_test_split(
    *arrays: Sequence[T] | NDArray[np.float64],
    test_size: float = 0.2,
    random_state: int = 0,
) -> list:
    """Split arrays into random train and test subsets.

    Examples
    --------
    >>> X = [1, 2, 3, 4, 5]
    >>> X_train, X_test = train_test_split(X, test_size=0.4, random_state=0)
    >>> len(X_train) + len(X_test)
    5
    """
    if not arrays:
        raise ValidationError("at least one array required")
    n = len(arrays[0])  # type: ignore[arg-type]
    for a in arrays:
        if len(a) != n:  # type: ignore[arg-type]
            raise ValidationError("all arrays must have the same length")
    rng = np.random.default_rng(random_state)
    idx = rng.permutation(n)
    n_test = max(1, int(n * test_size))
    test_idx = idx[:n_test]
    train_idx = idx[n_test:]
    out: list = []
    for a in arrays:
        a_arr = np.asarray(a)
        out.append(a_arr[train_idx])
        out.append(a_arr[test_idx])
    return out


def k_fold(
    n: int,
    k: int = 5,
    random_state: int = 0,
) -> list[tuple[NDArray[np.int32], NDArray[np.int32]]]:
    """Generate ``k`` (train_idx, test_idx) pairs for k-fold CV."""
    if k < 2:
        raise ValidationError("k must be ≥ 2")
    if n < k:
        raise ValidationError(f"n must be ≥ k (got n={n}, k={k})")
    rng = np.random.default_rng(random_state)
    idx = rng.permutation(n)
    folds = np.array_split(idx, k)
    splits: list[tuple[NDArray[np.int32], NDArray[np.int32]]] = []
    for i in range(k):
        test_idx = folds[i]
        train_idx = np.concatenate([folds[j] for j in range(k) if j != i])
        splits.append((train_idx, test_idx))
    return splits


__all__ = ["k_fold", "train_test_split"]

"""Evaluation metrics for ML."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from biokit.exceptions import ValidationError


def accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    """Classification accuracy.

    Examples
    --------
    >>> accuracy(["a", "b", "a"], ["a", "b", "b"])
    0.6666666666666666
    """
    if len(y_true) != len(y_pred):
        raise ValidationError("y_true and y_pred must have the same length")
    if not y_true:
        return 0.0
    correct = sum(1 for a, b in zip(y_true, y_pred, strict=True) if a == b)
    return correct / len(y_true)


def confusion_matrix(
    y_true: Sequence[str],
    y_pred: Sequence[str],
) -> tuple[list[str], NDArray[np.int32]]:
    """Return ``(labels, matrix)`` for the given predictions."""
    labels = sorted(set(y_true) | set(y_pred))
    idx = {l: i for i, l in enumerate(labels)}
    mat = np.zeros((len(labels), len(labels)), dtype=np.int32)
    for t, p in zip(y_true, y_pred, strict=True):
        mat[idx[t], idx[p]] += 1
    return labels, mat


def precision_recall_f1(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    positive_label: str,
) -> tuple[float, float, float]:
    """Return ``(precision, recall, F1)`` for ``positive_label``."""
    tp = fp = fn = 0
    for t, p in zip(y_true, y_pred, strict=True):
        if p == positive_label and t == positive_label:
            tp += 1
        elif p == positive_label and t != positive_label:
            fp += 1
        elif p != positive_label and t == positive_label:
            fn += 1
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1


def silhouette_score(
    X: NDArray[np.float64],
    labels: NDArray[np.int32],
) -> float:
    """Silhouette score for clustering (simplified)."""
    X = np.asarray(X, dtype=float)
    labels = np.asarray(labels)
    if len(X) != len(labels):
        raise ValidationError("X and labels must have the same length")
    if len(set(labels.tolist())) < 2:
        return 0.0
    n = len(X)
    sils: list[float] = []
    for i in range(n):
        same = labels == labels[i]
        same[i] = False
        if not same.any():
            continue
        a_i = np.sqrt(((X[same] - X[i]) ** 2).sum(axis=1)).mean()
        other_labels = set(labels.tolist()) - {labels[i]}
        b_i = min(
            np.sqrt(((X[labels == ol] - X[i]) ** 2).sum(axis=1)).mean()
            for ol in other_labels
            if (labels == ol).any()
        )
        sils.append((b_i - a_i) / max(a_i, b_i))
    return float(np.mean(sils)) if sils else 0.0


__all__ = ["accuracy", "confusion_matrix", "precision_recall_f1", "silhouette_score"]

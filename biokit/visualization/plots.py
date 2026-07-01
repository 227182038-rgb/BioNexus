"""Matplotlib-based plotting helpers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, cast

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from Bio.SeqRecord import SeqRecord

from biokit.exceptions import VisualizationError
from biokit.statistics.sequence_stats import gc_fraction

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def _get_or_create_fig_ax(
    ax: Axes | None,
) -> tuple[Figure, Axes]:
    """Return ``(fig, ax)`` — either from ``ax`` or a new figure."""
    if ax is None:
        fig, new_ax = plt.subplots(constrained_layout=True)
        return fig, new_ax
    # ``ax.figure`` is typed as ``Figure | SubFigure | None`` in matplotlib
    # stubs. In practice it is always set for non-embedded axes; we cast
    # rather than suppress because the alternative (returning Optional) would
    # force every caller to handle None.
    return cast(Figure, ax.figure), ax


def plot_gc_content(
    sequence: str,
    window: int = 100,
    step: int | None = None,
    title: str | None = None,
    ax: Axes | None = None,
) -> Figure:
    """Plot GC content across ``sequence`` using a sliding window."""
    if window < 1:
        raise VisualizationError("window must be ≥ 1")
    step = step or window
    positions: list[int] = []
    values: list[float] = []
    for i in range(0, len(sequence) - window + 1, step):
        positions.append(i + window // 2)
        values.append(gc_fraction(sequence[i : i + window]) * 100)
    fig, ax = _get_or_create_fig_ax(ax)
    ax.plot(positions, values, color="#2c7fb8", linewidth=1.5)
    ax.axhline(50, color="grey", linestyle=":", linewidth=0.8)
    ax.set_xlabel("Position (bp)")
    ax.set_ylabel("GC (%)")
    ax.set_title(title or "GC content")
    ax.set_ylim(0, 100)
    return fig


def plot_length_histogram(
    sequences: Iterable[SeqRecord],
    bins: int = 30,
    title: str | None = None,
    ax: Axes | None = None,
) -> Figure:
    """Plot a histogram of sequence lengths."""
    lengths: list[int] = [len(str(s.seq)) for s in sequences]
    if not lengths:
        raise VisualizationError("no sequences to plot")
    fig, ax = _get_or_create_fig_ax(ax)
    ax.hist(lengths, bins=bins, color="#31a354", edgecolor="white")
    ax.set_xlabel("Sequence length (bp)")
    ax.set_ylabel("Count")
    ax.set_title(title or "Sequence length distribution")
    return fig


def plot_composition_bar(
    sequence: str,
    title: str | None = None,
    ax: Axes | None = None,
) -> Figure:
    """Plot A/C/G/T composition as a bar chart."""
    seq = sequence.upper()
    counts = {b: seq.count(b) for b in "ACGT"}
    total = sum(counts.values()) or 1
    freqs = [counts[b] / total for b in "ACGT"]
    colors = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3"]
    fig, ax = _get_or_create_fig_ax(ax)
    ax.bar(list("ACGT"), freqs, color=colors, edgecolor="white")
    ax.set_ylabel("Frequency")
    ax.set_ylim(0, 1)
    ax.set_title(title or "Nucleotide composition")
    return fig


def plot_dotplot(
    seq_a: str,
    seq_b: str,
    window: int = 10,
    threshold: int | None = None,
    title: str | None = None,
    ax: Axes | None = None,
) -> Figure:
    """Plot a dotplot of two sequences."""
    seq_a = seq_a.upper()
    seq_b = seq_b.upper()
    threshold = threshold if threshold is not None else window
    fig, ax = _get_or_create_fig_ax(ax)
    xs: list[int] = []
    ys: list[int] = []
    for i in range(len(seq_a) - window + 1):
        for j in range(len(seq_b) - window + 1):
            matches = sum(
                1
                for a, b in zip(seq_a[i : i + window], seq_b[j : j + window], strict=True)
                if a == b
            )
            if matches >= threshold:
                xs.append(i)
                ys.append(j)
    ax.scatter(xs, ys, s=2, color="#000000")
    ax.set_xlabel("Sequence A position")
    ax.set_ylabel("Sequence B position")
    ax.set_title(title or "Dotplot")
    return fig


__all__ = [
    "plot_composition_bar",
    "plot_dotplot",
    "plot_gc_content",
    "plot_length_histogram",
]

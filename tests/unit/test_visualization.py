"""Tests for biokit.visualization."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from biokit.exceptions import VisualizationError
from biokit.visualization import (
    plot_composition_bar,
    plot_dotplot,
    plot_gc_content,
    plot_length_histogram,
)


def teardown_function(_):
    plt.close("all")


def test_plot_gc_content_returns_figure():
    fig = plot_gc_content("ATGC" * 100, window=20)
    assert fig is not None


def test_plot_gc_content_invalid_window():
    with pytest.raises(VisualizationError):
        plot_gc_content("ATGC" * 100, window=0)


def test_plot_length_histogram_basic():
    seqs = [SeqRecord(Seq("A" * n), id=f"seq{n}") for n in [100, 200, 300]]
    fig = plot_length_histogram(seqs)
    assert fig is not None


def test_plot_length_histogram_empty():
    with pytest.raises(VisualizationError):
        plot_length_histogram([])


def test_plot_composition_bar():
    fig = plot_composition_bar("ATGCATGCATGC")
    assert fig is not None


def test_plot_dotplot():
    fig = plot_dotplot("ATGCATGCATGC", "ATGCATGCATGC", window=4)
    assert fig is not None

"""Tests for biokit.crispr."""

from __future__ import annotations

from biokit.crispr import (
    DEFAULT_GUIDE_LENGTH,
    DEFAULT_PAM,
    GuideRNA,
    annotate_guides,
    design_guides,
    find_off_targets,
    iter_guides,
    score_guide,
)


def test_design_guides_returns_candidates():
    seq = "ATGGCAGGTGACCCGTTGACCGGTAACGCATGCAGTGGACCTAGG"
    guides = design_guides(seq)
    assert len(guides) > 0
    for g in guides:
        assert isinstance(g, GuideRNA)
        assert len(g.spacer) == DEFAULT_GUIDE_LENGTH
        assert g.pam.endswith("GG")
        assert g.strand in {"+", "-"}


def test_design_guides_no_pam():
    seq = "ATATATATATATATATATATATATATATATATATATATAT"
    assert design_guides(seq) == []


def test_iter_guides_yields_tuples():
    seq = "ATGGCAGGTGACCCGTTGACCGG"
    guides = list(iter_guides(seq))
    assert len(guides) > 0
    spacer, pam, pos, strand = guides[0]
    assert len(spacer) == DEFAULT_GUIDE_LENGTH
    assert len(pam) == len(DEFAULT_PAM)


def test_score_guide_no_offtargets_high():
    assert score_guide("ATGCATGCATGCATGCATGC", off_targets=0) > 0


def test_score_guide_poly_t_penalised():
    good = "ATGCATGCATGCATGCATGC"
    bad = "ATGCATGCATGCATGTTTTT"
    assert score_guide(good) > score_guide(bad)


def test_find_off_targets_excludes_on_target():
    target_seq = "ATGGCAGGTGACCCGTTGACCGG"
    guides = design_guides(target_seq)
    assert len(guides) > 0
    guide = guides[0]
    offs = find_off_targets(guide, target_seq, max_mismatches=0)
    assert offs == []


def test_annotate_guides_updates_off_targets():
    target_seq = "ATGGCAGGTGACCCGTTGACCGG"
    guides = design_guides(target_seq)
    annotated = annotate_guides(guides, target_seq)
    assert len(annotated) == len(guides)
    for g in annotated:
        assert isinstance(g.off_targets, list)


def test_default_constants():
    assert DEFAULT_PAM == "NGG"
    assert DEFAULT_GUIDE_LENGTH == 20

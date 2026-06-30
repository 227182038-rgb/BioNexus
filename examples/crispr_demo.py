"""Example: CRISPR sgRNA design."""

from __future__ import annotations

from biokit.crispr import annotate_guides, design_guides, find_off_targets


def main() -> None:
    target = (
        "ATGGCAGGTGACCCGTTGACCGGTAACGCATGCAGTGGACCTAGGACGTACGTTAAGGATGCAAATGGCAGGTGACCCGTGATAAGG"
    )
    print(f"Target ({len(target)} bp): {target}")
    guides = design_guides(target)
    print(f"Found {len(guides)} candidate guides. Top 5:")
    for g in guides[:5]:
        print(f"  {g.spacer} PAM={g.pam} strand={g.strand} GC={g.gc:.0%} score={g.score:.1f}")

    if guides:
        guide = guides[0]
        offs = find_off_targets(guide, target, max_mismatches=3)
        print(f"\nTop guide has {len(offs)} off-target sites in target")

    annotated = annotate_guides(guides, target, max_mismatches=3)
    print("\nAnnotated top 3:")
    for g in annotated[:3]:
        print(f"  {g.spacer} off_targets={len(g.off_targets)} score={g.score:.1f}")


if __name__ == "__main__":
    main()

"""Robinson-Foulds tree distance."""

from __future__ import annotations

from biokit.phylogeny.node import TreeNode
from biokit.phylogeny.tree import Tree


def _clades(node: TreeNode) -> set[frozenset[str]]:
    """Return the set of all clades (as frozensets of leaf names) below ``node``."""
    clades: set[frozenset[str]] = set()
    if node.is_leaf:
        return clades
    leaves = frozenset(l.name for l in node.leaves())
    clades.add(leaves)
    for c in node.children:
        clades.update(_clades(c))
    return clades


def robinson_foulds_distance(tree_a: Tree, tree_b: Tree) -> int:
    """Robinson-Foulds distance between two trees.

    The RF distance is the number of clades present in one tree but not the
    other, summed over both directions.
    """
    if {l.name for l in tree_a.leaves} != {l.name for l in tree_b.leaves}:
        raise ValueError("trees must have the same leaf set")
    ca = _clades(tree_a.root)
    cb = _clades(tree_b.root)
    return len(ca.symmetric_difference(cb))


__all__ = ["robinson_foulds_distance"]

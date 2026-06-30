"""Tree data model."""

from __future__ import annotations

from dataclasses import dataclass, field

from biokit.phylogeny.node import TreeNode


@dataclass
class Tree:
    """A phylogenetic tree."""

    root: TreeNode = field(default_factory=TreeNode)

    @property
    def leaves(self) -> list[TreeNode]:
        """All leaf nodes in the tree."""
        return self.root.leaves()

    @property
    def num_leaves(self) -> int:
        """Number of leaves."""
        return len(self.leaves)


__all__ = ["Tree"]

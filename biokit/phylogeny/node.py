"""Tree node data model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TreeNode:
    """A node in a phylogenetic tree."""

    name: str = ""
    branch_length: float = 0.0
    children: list[TreeNode] = field(default_factory=list)
    parent: TreeNode | None = None

    @property
    def is_leaf(self) -> bool:
        """True if this is a leaf node."""
        return not self.children

    @property
    def is_internal(self) -> bool:
        """True if this is an internal node."""
        return bool(self.children)

    def add_child(self, child: TreeNode) -> TreeNode:
        """Add a child node and return it."""
        child.parent = self
        self.children.append(child)
        return child

    def leaves(self) -> list[TreeNode]:
        """Return all leaf descendants (including self if leaf)."""
        if self.is_leaf:
            return [self]
        out: list[TreeNode] = []
        for c in self.children:
            out.extend(c.leaves())
        return out


__all__ = ["TreeNode"]

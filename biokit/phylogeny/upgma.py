"""UPGMA tree builder."""

from __future__ import annotations

from biokit.phylogeny.node import TreeNode
from biokit.phylogeny.tree import Tree


class UPGMA:
    """Unweighted Pair Group Method with Arithmetic Mean.

    Builds a rooted tree from a distance matrix.

    Examples
    --------
    >>> taxa = ["A", "B", "C"]
    >>> matrix = [[0, 1, 2], [1, 0, 3], [2, 3, 0]]
    >>> tree = UPGMA().build(taxa, matrix)
    >>> tree.num_leaves
    3
    """

    def build(self, taxa: list[str], matrix: list[list[float]]) -> Tree:
        """Build a UPGMA tree from a distance matrix."""
        if len(taxa) != len(matrix) or any(len(row) != len(taxa) for row in matrix):
            raise ValueError("matrix dimensions must match taxa")
        nodes: list[TreeNode] = [TreeNode(name=t) for t in taxa]
        sizes: list[int] = [1] * len(taxa)
        dist = [row[:] for row in matrix]
        while len(nodes) > 1:
            # Find closest pair
            min_i, min_j, min_d = 0, 1, float("inf")
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    if dist[i][j] < min_d:
                        min_d = dist[i][j]
                        min_i, min_j = i, j
            # Create new node
            new_node = TreeNode(branch_length=0.0)
            bl = min_d / 2.0
            child_i = nodes[min_i]
            child_j = nodes[min_j]
            object.__setattr__(child_i, "branch_length", bl - (child_i.branch_length or 0))
            object.__setattr__(child_j, "branch_length", bl - (child_j.branch_length or 0))
            new_node.add_child(child_i)
            new_node.add_child(child_j)
            # Update distances
            new_size = sizes[min_i] + sizes[min_j]
            new_dist: list[float] = []
            for k in range(len(nodes)):
                if k in (min_i, min_j):
                    continue
                d = (sizes[min_i] * dist[min_i][k] + sizes[min_j] * dist[min_j][k]) / new_size
                new_dist.append(d)
            # Remove old nodes, add new
            keep = [k for k in range(len(nodes)) if k != min_i and k != min_j]
            nodes = [nodes[k] for k in keep] + [new_node]
            sizes = [sizes[k] for k in keep] + [new_size]
            new_matrix = [[dist[a][b] for b in keep] for a in keep]
            new_matrix.append([*new_dist, 0.0])
            for idx, d in enumerate(new_dist):
                new_matrix[idx].append(d)
            dist = new_matrix
        return Tree(root=nodes[0])


__all__ = ["UPGMA"]

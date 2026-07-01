"""Newick format parser and writer."""

from __future__ import annotations

from biokit.phylogeny.node import TreeNode


def _node_to_newick(node: TreeNode, is_root: bool = True) -> str:
    if node.is_leaf:
        suffix = node.name
    else:
        parts = [_node_to_newick(c, is_root=False) for c in node.children]
        suffix = "(" + ",".join(parts) + ")"
    if node.branch_length:
        suffix += f":{node.branch_length}"
    # Internal node name is appended after the closing paren, but only if non-empty
    # and only for non-root nodes (root names are usually omitted in standard Newick)
    if not node.is_leaf and node.name and not is_root:
        suffix = suffix + node.name
    return suffix


def write_newick(node: TreeNode) -> str:
    """Render a tree as a Newick string.

    Examples
    --------
    >>> root = TreeNode(name="root")
    >>> root.add_child(TreeNode(name="A", branch_length=0.1))
    >>> root.add_child(TreeNode(name="B", branch_length=0.2))
    >>> write_newick(root)
    '(A:0.1,B:0.2);'
    """
    return _node_to_newick(node, is_root=True) + ";"


def parse_newick(text: str) -> TreeNode:
    """Parse a Newick string into a tree.

    Note: this is a minimal parser supporting names, branch lengths, and
    nested parentheses. For full Newick (with quoted labels, comments, etc.)
    use Biopython's :mod:`Bio.Phylo`.
    """
    text = text.strip().rstrip(";")
    if not text:
        return TreeNode()
    return _parse_node(text)


def _parse_node(text: str) -> TreeNode:
    text = text.strip()
    if not text.startswith("("):
        # Leaf
        if ":" in text:
            name, bl = text.split(":", 1)
            return TreeNode(name=name, branch_length=float(bl))
        return TreeNode(name=text)
    # Find matching close paren
    depth = 0
    close_idx = -1
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                close_idx = i
                break
    inner = text[1:close_idx]
    rest = text[close_idx + 1 :]
    # Parse children
    children: list[TreeNode] = []
    depth = 0
    start = 0
    for i, ch in enumerate(inner):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            children.append(_parse_node(inner[start:i]))
            start = i + 1
    children.append(_parse_node(inner[start:]))
    # Parse internal name and branch length
    node_name = ""
    node_bl: float = 0.0
    if rest:
        if ":" in rest:
            node_name, bl_str = rest.split(":", 1)
            node_name = node_name.strip()
            node_bl = float(bl_str)
        else:
            node_name = rest.strip()
    node = TreeNode(name=node_name, branch_length=node_bl)
    for child in children:
        node.add_child(child)
    return node


__all__ = ["parse_newick", "write_newick"]

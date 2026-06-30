"""Tests for biokit.phylogeny and biokit.restriction."""

from __future__ import annotations

from biokit.phylogeny import (
    UPGMA,
    Tree,
    TreeNode,
    parse_newick,
    robinson_foulds_distance,
    write_newick,
)
from biokit.restriction import Enzyme, RestrictionEnzymeDatabase, cut_site


class TestTreeNode:
    """TreeNode tests."""

    def test_leaf_and_internal(self):
        leaf = TreeNode(name="A")
        assert leaf.is_leaf
        assert not leaf.is_internal

        internal = TreeNode(name="root")
        internal.add_child(TreeNode(name="A"))
        assert internal.is_internal
        assert not internal.is_leaf
        assert len(internal.leaves()) == 1


class TestNewick:
    """Newick parser/writer tests."""

    def test_write_simple(self):
        root = TreeNode(name="root")
        root.add_child(TreeNode(name="A", branch_length=0.1))
        root.add_child(TreeNode(name="B", branch_length=0.2))
        assert write_newick(root) == "(A:0.1,B:0.2);"

    def test_parse_simple(self):
        tree = parse_newick("(A:0.1,B:0.2);")
        assert len(tree.children) == 2
        assert tree.children[0].name == "A"
        assert tree.children[0].branch_length == 0.1


class TestUPGMA:
    """UPGMA tests."""

    def test_build_tree(self):
        taxa = ["A", "B", "C"]
        matrix = [[0, 1, 2], [1, 0, 3], [2, 3, 0]]
        tree = UPGMA().build(taxa, matrix)
        assert tree.num_leaves == 3


class TestRobinsonFoulds:
    """Robinson-Foulds distance tests."""

    def test_identical_trees(self):
        t1 = parse_newick("((A,B),C);")
        t2 = parse_newick("((A,B),C);")
        tree1 = Tree(root=t1)
        tree2 = Tree(root=t2)
        assert robinson_foulds_distance(tree1, tree2) == 0

    def test_different_trees(self):
        t1 = Tree(root=parse_newick("((A,B),(C,D));"))
        t2 = Tree(root=parse_newick("((A,C),(B,D));"))
        assert robinson_foulds_distance(t1, t2) > 0


class TestRestriction:
    """Restriction enzyme tests."""

    def test_database_lookup(self):
        db = RestrictionEnzymeDatabase()
        e = db.get("EcoRI")
        assert e.recognition_site == "GAATTC"

    def test_cut_site(self):
        e = Enzyme("EcoRI", "GAATTC", 1)
        positions = cut_site(e, "GAATTCAAAGAATTC")
        assert positions == [1, 10]

    def test_cut_site_no_match(self):
        e = Enzyme("EcoRI", "GAATTC", 1)
        assert cut_site(e, "GGGGGGG") == []

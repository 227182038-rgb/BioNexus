"""End-to-end integration tests for the BioNexus bridge.

These tests exercise the full stack: NEXUS orchestrator → bridge → BioKit 2.0
programs. They use the DummyProvider so no real LLM credentials are required.
"""

from __future__ import annotations

import pytest
from bridge import list_biokit_programs, quickstart
from bridge.biokit_programs import PROGRAMS, BioKitProgramRegistry, register_all
from nexus.core.biokit import InProcessBioKit
from nexus.core.types import EvidenceClass

# ---------------------------------------------------------------------------
# Bridge setup tests
# ---------------------------------------------------------------------------


class TestBridgeSetup:
    """Verify the bridge wiring is correct."""

    def test_quickstart_returns_nexus(self):
        nx = quickstart()
        from nexus.sdk import Nexus

        assert isinstance(nx, Nexus)

    def test_quickstart_registers_all_programs(self):
        nx = quickstart()
        registered = set(nx.biokit.list_programs())
        expected = set(PROGRAMS.keys())
        assert registered == expected

    def test_list_biokit_programs_returns_sorted(self):
        programs = list_biokit_programs()
        assert programs == sorted(programs)
        assert len(programs) >= 22

    def test_register_all_is_idempotent_failure(self):
        """register_all should refuse to double-register."""
        bk = InProcessBioKit()
        register_all(bk)
        with pytest.raises(ValueError, match="already registered"):
            register_all(bk)

    def test_registry_get_unknown_raises(self):
        with pytest.raises(KeyError, match="unknown BioKit program"):
            BioKitProgramRegistry.get("nonexistent_program")


# ---------------------------------------------------------------------------
# BioKit program invocation tests
# ---------------------------------------------------------------------------


class TestBioKitPrograms:
    """Verify each BioKit program runs through the bridge correctly."""

    @pytest.fixture
    def nx(self):
        return quickstart()

    def test_gc_content(self, nx):
        out = nx.run_biokit("gc_content", {"sequence": "ATGGCAGGTGACCCGTGA"})
        assert out.outputs["gc_fraction"] == pytest.approx(0.6111, abs=0.001)
        assert out.outputs["gc_percentage"] == pytest.approx(61.11, abs=0.1)
        assert out.outputs["length"] == 18

    def test_transcribe(self, nx):
        out = nx.run_biokit("transcribe", {"sequence": "ATGGCAGGT"})
        assert out.outputs["rna"] == "AUGGCAGGU"

    def test_reverse_transcribe(self, nx):
        out = nx.run_biokit("reverse_transcribe", {"sequence": "AUGGCAGGU"})
        assert out.outputs["dna"] == "ATGGCAGGT"

    def test_translate(self, nx):
        out = nx.run_biokit("translate", {"sequence": "ATGGCAGGTGACCCGTGA"})
        assert out.outputs["protein"] == "MAGDP"

    def test_find_orfs(self, nx):
        out = nx.run_biokit(
            "find_orfs",
            {"sequence": "ATGGCAGGTGACCCGTGA", "minimum_length": 6},
        )
        assert out.outputs["count"] >= 1
        assert out.outputs["orfs"][0]["protein_sequence"] == "MAGDP"

    def test_needleman_wunsch(self, nx):
        out = nx.run_biokit(
            "needleman_wunsch",
            {"seq1": "GATTACA", "seq2": "GCATGCU"},
        )
        assert out.outputs["length"] > 0
        assert out.outputs["matches"] > 0

    def test_smith_waterman(self, nx):
        out = nx.run_biokit(
            "smith_waterman",
            {"seq1": "ACGTACGT", "seq2": "ACGT"},
        )
        assert out.outputs["score"] > 0
        assert "ACGT" in out.outputs["aligned_seq1"]

    def test_gotoh(self, nx):
        out = nx.run_biokit(
            "gotoh",
            {"seq1": "ACGTACGT", "seq2": "ACGTACGT"},
        )
        assert out.outputs["matches"] > 0

    def test_debruijn_assemble(self, nx):
        out = nx.run_biokit(
            "debruijn_assemble",
            {
                "reads": ["ATGGCAGGTGAC", "GCAGGTGACCCG", "GGTGACCCGTTGA"],
                "k": 5,
            },
        )
        assert out.outputs["num_contigs"] >= 1
        assert out.outputs["n50"] > 0
        assert 0.0 <= out.outputs["gc"] <= 1.0

    def test_design_primer(self, nx):
        out = nx.run_biokit(
            "design_primer",
            {"template": "ATGGCAGGTGACCCGTTGACCGTACGTAACGCATGCAGT", "length": 20},
        )
        assert out.outputs["count"] > 0
        primer = out.outputs["primers"][0]
        assert len(primer["sequence"]) == 20
        assert 0.0 <= primer["gc"] <= 1.0

    def test_tm_nearest_neighbor(self, nx):
        out = nx.run_biokit(
            "tm",
            {"sequence": "GTAAAACGACGGCCAGT", "method": "nearest_neighbor"},
        )
        assert 30 < out.outputs["tm"] < 80
        assert out.outputs["method"] == "nearest_neighbor"

    def test_tm_wallace(self, nx):
        out = nx.run_biokit(
            "tm",
            {"sequence": "ATGCATGC", "method": "wallace"},
        )
        assert out.outputs["tm"] == 24.0

    def test_design_guides(self, nx):
        out = nx.run_biokit(
            "design_guides",
            {"sequence": "ATGGCAGGTGACCCGTTGACCGGTAACGCATGCAGTGGACCTAGG"},
        )
        assert out.outputs["count"] > 0
        guide = out.outputs["guides"][0]
        assert len(guide["spacer"]) == 20
        assert guide["pam"].endswith("GG")

    def test_find_off_targets(self, nx):
        # First design a guide, then search for off-targets
        guides_out = nx.run_biokit(
            "design_guides",
            {"sequence": "ATGGCAGGTGACCCGTTGACCGG"},
        )
        guide = guides_out.outputs["guides"][0]
        out = nx.run_biokit(
            "find_off_targets",
            {"guide": guide, "reference": "ATGGCAGGTGACCCGTTGACCGG", "max_mismatches": 0},
        )
        # On-target should be excluded
        assert out.outputs["count"] == 0

    def test_parse_blast_xml(self, nx):
        out = nx.run_biokit(
            "parse_blast_xml",
            {"path": "tests/data/blast_sample.xml"},
        )
        assert out.outputs["total_hits"] >= 1
        record = out.outputs["records"][0]
        assert record["query_id"] == "query1"

    def test_parse_fasta(self, nx):
        out = nx.run_biokit(
            "parse_fasta",
            {"source": "tests/data/sample.fasta"},
        )
        assert out.outputs["count"] == 3

    def test_parse_gff3(self, nx):
        out = nx.run_biokit(
            "parse_gff3",
            {"source": "tests/data/sample.gff3"},
        )
        assert out.outputs["count"] >= 1
        assert out.outputs["features"][0]["type"] == "gene"

    def test_parse_bed(self, nx):
        out = nx.run_biokit(
            "parse_bed",
            {"source": "tests/data/sample.bed"},
        )
        assert out.outputs["count"] == 2

    def test_allele_stats(self, nx):
        out = nx.run_biokit(
            "allele_stats",
            {"genotypes": [["A", "A"], ["A", "a"], ["a", "a"]]},
        )
        assert out.outputs["num_genotypes"] == 3
        assert out.outputs["num_alleles"] == 2
        assert out.outputs["expected_heterozygosity"] == pytest.approx(0.5)

    def test_hardy_weinberg_test(self, nx):
        genotypes = [["A", "A"]] * 25 + [["A", "a"]] * 50 + [["a", "a"]] * 25
        out = nx.run_biokit("hardy_weinberg_test", {"genotypes": genotypes})
        assert 0.0 <= out.outputs["p_value"] <= 1.0

    def test_fst(self, nx):
        out = nx.run_biokit(
            "fst",
            {
                "populations": [
                    [["A", "A"], ["A", "a"], ["a", "a"]],
                    [["A", "A"], ["A", "A"], ["A", "a"]],
                ]
            },
        )
        assert -1.0 < out.outputs["fst"] < 1.0

    def test_restriction_cut(self, nx):
        out = nx.run_biokit(
            "restriction_cut",
            {"enzyme_name": "EcoRI", "sequence": "GAATTCAAAGAATTC"},
        )
        assert out.outputs["count"] == 2

    def test_sequence_complexity(self, nx):
        out = nx.run_biokit(
            "sequence_complexity",
            {"sequence": "AAAAAA"},
        )
        assert out.outputs["complexity"] == 0.0

    def test_kmer_count(self, nx):
        out = nx.run_biokit(
            "kmer_count",
            {"sequence": "ATGCATGCAT", "k": 3},
        )
        assert out.outputs["unique_count"] > 0
        assert out.outputs["total_count"] > 0


# ---------------------------------------------------------------------------
# Evidence ledger integration tests
# ---------------------------------------------------------------------------


class TestEvidenceLedger:
    """Verify BioKit outputs enter the NEXUS evidence ledger correctly."""

    def test_biokit_output_registered_as_evidence(self):
        nx = quickstart()
        initial_count = len(nx.engine.evidence_ledger.entries)
        nx.run_biokit("gc_content", {"sequence": "ATGGCAGGT"})
        assert len(nx.engine.evidence_ledger.entries) == initial_count + 1

    def test_evidence_class_is_deterministic(self):
        nx = quickstart()
        out = nx.run_biokit("gc_content", {"sequence": "ATGGCAGGT"})
        evidence = out.as_evidence()
        assert evidence.source_class == EvidenceClass.DETERMINISTIC

    def test_evidence_is_content_addressed(self):
        """Same inputs → same fingerprint (idempotent)."""
        nx = quickstart()
        out1 = nx.run_biokit("gc_content", {"sequence": "ATGGCAGGT"})
        out2 = nx.run_biokit("gc_content", {"sequence": "ATGGCAGGT"})
        assert out1.fingerprint == out2.fingerprint

    def test_different_inputs_different_fingerprint(self):
        nx = quickstart()
        out1 = nx.run_biokit("gc_content", {"sequence": "ATGGCAGGT"})
        out2 = nx.run_biokit("gc_content", {"sequence": "ATGGCAGGTA"})
        assert out1.fingerprint != out2.fingerprint


# ---------------------------------------------------------------------------
# NEXUS agent + BioKit integration tests
# ---------------------------------------------------------------------------


class TestAgentBioKitIntegration:
    """Verify NEXUS agents can consume BioKit outputs as context."""

    def test_literature_agent_with_biokit_context(self):
        """The literature agent should accept a BioKit output as context."""
        nx = quickstart()
        biokit_out = nx.run_biokit("gc_content", {"sequence": "ATGGCAGGTGACCCGTGA"})
        result = nx.interpret(
            "What does this GC content suggest?",
            agent="literature",
            context={"biokit_output": biokit_out.outputs},
        )
        assert result is not None
        assert result.answer  # non-empty

    def test_all_agents_listed(self):
        nx = quickstart()
        agents = nx.list_agents()
        assert "literature" in agents
        assert "validation" in agents
        assert "experiment" in agents
        assert "workflow" in agents
        assert "report" in agents

    def test_run_biokit_unknown_program_raises(self):
        nx = quickstart()
        with pytest.raises(KeyError):
            nx.run_biokit("nonexistent_program", {})

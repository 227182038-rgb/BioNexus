"""BioKit 2.0 → NEXUS BioKitProgram adapters.

Each class here wraps a BioKit 2.0 function/class as a NEXUS
:class:`nexus.core.biokit.BioKitProgram`. The wrapper is responsible for:

1. Translating the dict-typed ``inputs`` argument into BioKit's native
   Python API.
2. Invoking the deterministic BioKit computation.
3. Translating the BioKit result object back into a dict of named outputs.

All BioKit computations are deterministic: given identical inputs they
produce bit-identical outputs. The wrapper therefore does NOT introduce any
non-determinism (no random seeds without explicit input, no wall-clock
calls, no network access).

Adding a new BioKit module to NEXUS = adding one class here + one entry
in ``PROGRAMS``.
"""

from __future__ import annotations

from typing import Any

# BioKit 2.0 imports — the only place NEXUS touches BioKit internals.
from biokit.alignment import GotohAligner, NeedlemanWunsch, SmithWaterman
from biokit.assembly import DeBruijnAssembler, assembly_gc, l50, n50
from biokit.blast import filter_hits, parse_blast_xml
from biokit.crispr import design_guides, find_off_targets
from biokit.io import parse_bed, parse_fasta, parse_gff3
from biokit.kmers import KmerCounter
from biokit.orf import ORFFinder
from biokit.popgen import (
    allele_stats,
    hardy_weinberg_test,
    weir_cockerham_fst,
)
from biokit.primer import design_primer, tm_gc, tm_nearest_neighbor, tm_wallace
from biokit.restriction import RestrictionEnzymeDatabase, cut_site
from biokit.rna import reverse_transcribe, transcribe
from biokit.statistics.sequence_stats import gc_fraction, sequence_complexity
from biokit.translation import Translator
from nexus.core.biokit import InProcessBioKit

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _to_fasta_records(records: list[Any]) -> list[dict[str, Any]]:
    """Serialise a list of BioKit FastaRecord (NamedTuples) to dicts."""
    return [{"id": r.id, "description": r.description, "sequence": r.sequence} for r in records]


def _to_gff3_features(features: list[Any]) -> list[dict[str, Any]]:
    """Serialise GFF3Feature dataclass instances to dicts."""
    return [
        {
            "seqid": f.seqid,
            "source": f.source,
            "type": f.type,
            "start": f.start,
            "end": f.end,
            "score": f.score,
            "strand": f.strand,
            "phase": f.phase,
            "attributes": dict(f.attributes),
            "length": f.length,
        }
        for f in features
    ]


def _to_bed_features(features: list[Any]) -> list[dict[str, Any]]:
    """Serialise BEDFeature dataclass instances to dicts."""
    return [
        {
            "chrom": f.chrom,
            "start": f.start,
            "end": f.end,
            "name": f.name,
            "score": f.score,
            "strand": f.strand,
            "length": f.length,
        }
        for f in features
    ]


# ---------------------------------------------------------------------------
# Base class for all program wrappers
# ---------------------------------------------------------------------------


class ProgramWrapper:
    """Base class for BioKit program wrappers.

    Every subclass defines a ``name`` class attribute and a ``run`` method
    that takes ``dict[str, Any]`` and returns ``dict[str, Any]``. This base
    class gives the registry a concrete type to work with, avoiding
    ``type: ignore`` comments at call sites.

    The ``run`` method signature matches the :class:`nexus.core.biokit.BioKitProgram`
    protocol, so ``ProgramWrapper`` instances can be registered directly
    with :meth:`InProcessBioKit.register_program`.
    """

    name: str = ""

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Execute the BioKit program. Override in subclasses."""
        raise NotImplementedError(
            f"{type(self).__name__} does not implement run(); subclasses must override this method."
        )


# ---------------------------------------------------------------------------
# Sequence programs
# ---------------------------------------------------------------------------


class GCContentProgram(ProgramWrapper):
    """Compute GC fraction of a DNA or RNA sequence.

    Inputs:
        sequence : str
    Outputs:
        gc_fraction : float (0..1)
        gc_percentage : float (0..100)
        length : int
    """

    name = "gc_content"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        seq: str = inputs["sequence"]
        gc = gc_fraction(seq)
        return {
            "gc_fraction": gc,
            "gc_percentage": gc * 100.0,
            "length": len(seq),
        }


class TranscribeProgram(ProgramWrapper):
    """Transcribe DNA to mRNA (T → U).

    Inputs:
        sequence : str (DNA)
    Outputs:
        rna : str
    """

    name = "transcribe"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        return {"rna": transcribe(inputs["sequence"])}


class ReverseTranscribeProgram(ProgramWrapper):
    """Reverse-transcribe RNA to DNA (U → T).

    Inputs:
        sequence : str (RNA)
    Outputs:
        dna : str
    """

    name = "reverse_transcribe"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        return {"dna": reverse_transcribe(inputs["sequence"])}


class TranslateProgram(ProgramWrapper):
    """Translate a nucleotide sequence to a protein.

    Inputs:
        sequence : str
        frame : int (1, 2, or 3; default 1)
        stop_at_stop : bool (default True)
    Outputs:
        protein : str
    """

    name = "translate"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        protein = Translator().translate(
            inputs["sequence"],
            frame=inputs.get("frame", 1),
            stop_at_stop=inputs.get("stop_at_stop", True),
        )
        return {"protein": protein}


# ---------------------------------------------------------------------------
# ORF programs
# ---------------------------------------------------------------------------


class FindOrfsProgram(ProgramWrapper):
    """Find open reading frames in six frames.

    Inputs:
        sequence : str
        minimum_length : int (default 30)
    Outputs:
        orfs : list[dict] with keys start, end, frame, strand,
               nucleotide_sequence, protein_sequence
        count : int
    """

    name = "find_orfs"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        orfs = ORFFinder(minimum_length=inputs.get("minimum_length", 30)).find(inputs["sequence"])
        serialised = [
            {
                "start": o.start,
                "end": o.end,
                "frame": o.frame,
                "strand": o.strand,
                "nucleotide_sequence": o.nucleotide_sequence,
                "protein_sequence": o.protein_sequence,
                "length": o.length,
            }
            for o in orfs
        ]
        return {"orfs": serialised, "count": len(serialised)}


# ---------------------------------------------------------------------------
# Alignment programs
# ---------------------------------------------------------------------------


class NeedlemanWunschProgram(ProgramWrapper):
    """Global sequence alignment (Needleman-Wunsch).

    Inputs:
        seq1, seq2 : str
        match, mismatch, gap : int (defaults 1, -1, -2)
    Outputs:
        score, aligned_seq1, aligned_seq2, matches, mismatches, gaps,
        identity, length
    """

    name = "needleman_wunsch"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        result = NeedlemanWunsch(
            match=inputs.get("match", 1),
            mismatch=inputs.get("mismatch", -1),
            gap=inputs.get("gap", -2),
        ).align(inputs["seq1"], inputs["seq2"])
        return {
            "score": result.score,
            "aligned_seq1": result.aligned_seq1,
            "aligned_seq2": result.aligned_seq2,
            "matches": result.matches,
            "mismatches": result.mismatches,
            "gaps": result.gaps,
            "identity": result.identity,
            "length": result.length,
        }


class SmithWatermanProgram(ProgramWrapper):
    """Local sequence alignment (Smith-Waterman).

    Inputs/Outputs: same as NeedlemanWunschProgram.
    """

    name = "smith_waterman"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        result = SmithWaterman(
            match=inputs.get("match", 2),
            mismatch=inputs.get("mismatch", -1),
            gap=inputs.get("gap", -2),
        ).align(inputs["seq1"], inputs["seq2"])
        return {
            "score": result.score,
            "aligned_seq1": result.aligned_seq1,
            "aligned_seq2": result.aligned_seq2,
            "matches": result.matches,
            "mismatches": result.mismatches,
            "gaps": result.gaps,
            "identity": result.identity,
            "length": result.length,
        }


class GotohProgram(ProgramWrapper):
    """Global alignment with affine gap penalties (Gotoh).

    Inputs:
        seq1, seq2 : str
        match, mismatch, gap_open, gap_extend : int (defaults 1, -1, -5, -1)
    Outputs: same as NeedlemanWunschProgram.
    """

    name = "gotoh"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        result = GotohAligner(
            match=inputs.get("match", 1),
            mismatch=inputs.get("mismatch", -1),
            gap_open=inputs.get("gap_open", -5),
            gap_extend=inputs.get("gap_extend", -1),
        ).align(inputs["seq1"], inputs["seq2"])
        return {
            "score": result.score,
            "aligned_seq1": result.aligned_seq1,
            "aligned_seq2": result.aligned_seq2,
            "matches": result.matches,
            "mismatches": result.mismatches,
            "gaps": result.gaps,
            "identity": result.identity,
            "length": result.length,
        }


# ---------------------------------------------------------------------------
# Assembly programs
# ---------------------------------------------------------------------------


class DeBruijnAssembleProgram(ProgramWrapper):
    """Assemble reads using a De Bruijn graph.

    Inputs:
        reads : list[str]
        k : int (default 21)
    Outputs:
        contigs : list[dict] with id, sequence, length
        num_contigs, total_length, longest_contig, n50, l50, gc
    """

    name = "debruijn_assemble"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        result = DeBruijnAssembler(k=inputs.get("k", 21)).assemble(inputs["reads"])
        contigs = [
            {"id": c.id, "sequence": str(c.seq), "length": len(str(c.seq))} for c in result.contigs
        ]
        return {
            "contigs": contigs,
            "num_contigs": result.num_contigs,
            "total_length": result.total_length,
            "longest_contig": result.longest_contig,
            "n50": n50(result.contigs),
            "l50": l50(result.contigs),
            "gc": assembly_gc(result.contigs),
        }


# ---------------------------------------------------------------------------
# Primer design programs
# ---------------------------------------------------------------------------


class DesignPrimerProgram(ProgramWrapper):
    """Design PCR primers for a template.

    Inputs:
        template : str
        length : int (default 20)
        tm_target : float (default 60.0)
        gc_min, gc_max : float (defaults 0.4, 0.6)
        max_self_comp : int (default 4)
        min_score : float (default 0.0)
        scan_reverse : bool (default True)
    Outputs:
        primers : list[dict] with sequence, start, end, strand, tm, gc,
                  self_comp, gc_clamp, score
        count : int
    """

    name = "design_primer"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        primers = design_primer(
            inputs["template"],
            length=inputs.get("length", 20),
            tm_target=inputs.get("tm_target", 60.0),
            gc_min=inputs.get("gc_min", 0.4),
            gc_max=inputs.get("gc_max", 0.6),
            max_self_comp=inputs.get("max_self_comp", 4),
            min_score=inputs.get("min_score", 0.0),
            scan_reverse=inputs.get("scan_reverse", True),
        )
        serialised = [
            {
                "sequence": p.sequence,
                "start": p.start,
                "end": p.end,
                "strand": p.strand,
                "tm": p.tm,
                "gc": p.gc,
                "self_comp": p.self_comp,
                "gc_clamp": p.gc_clamp,
                "score": p.score,
            }
            for p in primers
        ]
        return {"primers": serialised, "count": len(serialised)}


class TmProgram(ProgramWrapper):
    """Compute melting temperature using one of three methods.

    Inputs:
        sequence : str
        method : str ("wallace" | "gc" | "nearest_neighbor")
                 default "nearest_neighbor"
        na_conc : float (default 50.0, mM)
        primer_conc : float (default 250.0, nM)
    Outputs:
        tm : float (°C)
        method : str
    """

    name = "tm"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        method = inputs.get("method", "nearest_neighbor")
        if method == "wallace":
            tm = tm_wallace(inputs["sequence"])
        elif method == "gc":
            tm = tm_gc(inputs["sequence"], na_conc=inputs.get("na_conc", 50.0))
        elif method == "nearest_neighbor":
            tm = tm_nearest_neighbor(
                inputs["sequence"],
                na_conc=inputs.get("na_conc", 50.0),
                primer_conc=inputs.get("primer_conc", 250.0),
            )
        else:
            raise ValueError(f"unknown Tm method: {method!r}")
        return {"tm": tm, "method": method}


# ---------------------------------------------------------------------------
# CRISPR programs
# ---------------------------------------------------------------------------


class DesignGuidesProgram(ProgramWrapper):
    """Design CRISPR sgRNAs for a target sequence.

    Inputs:
        sequence : str
        guide_length : int (default 20)
        pam_pattern : str (default "NGG")
        min_score : float (default 0.0)
    Outputs:
        guides : list[dict] with spacer, pam, strand, position, gc, score
        count : int
    """

    name = "design_guides"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        guides = design_guides(
            inputs["sequence"],
            guide_length=inputs.get("guide_length", 20),
            pam_pattern=inputs.get("pam_pattern", "NGG"),
            min_score=inputs.get("min_score", 0.0),
        )
        serialised = [
            {
                "spacer": g.spacer,
                "pam": g.pam,
                "strand": g.strand,
                "position": g.position,
                "gc": g.gc,
                "score": g.score,
            }
            for g in guides
        ]
        return {"guides": serialised, "count": len(serialised)}


class FindOffTargetsProgram(ProgramWrapper):
    """Find off-target sites for a guide RNA.

    Inputs:
        guide : dict with at minimum 'spacer' (and optionally other GuideRNA fields)
        reference : str
        max_mismatches : int (default 3)
    Outputs:
        off_targets : list[dict] with sequence, position, strand, mismatches
        count : int
    """

    name = "find_off_targets"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        # Reconstruct a minimal GuideRNA-like object for the finder.
        # find_off_targets only reads .spacer, .position, .strand from the guide.
        from biokit.crispr.models import GuideRNA

        guide_input = inputs["guide"]
        guide = GuideRNA(
            spacer=guide_input["spacer"],
            pam=guide_input.get("pam", "NGG"),
            strand=guide_input.get("strand", "+"),
            position=guide_input.get("position", 1),
            gc=guide_input.get("gc", 0.5),
            score=guide_input.get("score", 0.0),
        )
        offs = find_off_targets(
            guide,
            inputs["reference"],
            max_mismatches=inputs.get("max_mismatches", 3),
        )
        serialised = [
            {
                "sequence": o.sequence,
                "position": o.position,
                "strand": o.strand,
                "mismatches": o.mismatches,
            }
            for o in offs
        ]
        return {"off_targets": serialised, "count": len(serialised)}


# ---------------------------------------------------------------------------
# BLAST programs
# ---------------------------------------------------------------------------


class ParseBlastXmlProgram(ProgramWrapper):
    """Parse a BLAST XML result file.

    Inputs:
        path : str
        max_evalue : float (optional, default no filter)
        min_identity : float (optional, default 0)
    Outputs:
        records : list[dict]
        total_hits : int
    """

    name = "parse_blast_xml"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        records = parse_blast_xml(inputs["path"])
        if "max_evalue" in inputs or "min_identity" in inputs:
            records = filter_hits(
                records,
                max_evalue=inputs.get("max_evalue", 1e-5),
                min_identity=inputs.get("min_identity", 0.0),
            )
        serialised: list[dict[str, Any]] = [
            {
                "query_id": r.query_id,
                "query_length": r.query_length,
                "hits": [
                    {
                        "subject_id": h.subject_id,
                        "subject_title": h.subject_title,
                        "subject_length": h.subject_length,
                        "best_evalue": h.best_evalue,
                        "best_score": h.best_score,
                        "hsps": [
                            {
                                "query_start": hsp.query_start,
                                "query_end": hsp.query_end,
                                "subject_start": hsp.subject_start,
                                "subject_end": hsp.subject_end,
                                "score": hsp.score,
                                "evalue": hsp.evalue,
                                "identity": hsp.identity,
                                "alignment_length": hsp.alignment_length,
                                "percent_identity": hsp.percent_identity,
                            }
                            for hsp in h.hsps
                        ],
                    }
                    for h in r.hits
                ],
            }
            for r in records
        ]
        total_hits = sum(len(r["hits"]) for r in serialised)
        return {"records": serialised, "total_hits": total_hits}


# ---------------------------------------------------------------------------
# I/O programs
# ---------------------------------------------------------------------------


class ParseFastaProgram(ProgramWrapper):
    """Parse a FASTA file or text.

    Inputs:
        source : str (path or raw text starting with '>')
    Outputs:
        records : list[dict] with id, description, sequence
        count : int
    """

    name = "parse_fasta"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        records = list(parse_fasta(inputs["source"]))
        return {"records": _to_fasta_records(records), "count": len(records)}


class ParseGff3Program(ProgramWrapper):
    """Parse a GFF3 file or text.

    Inputs:
        source : str (path or raw text)
    Outputs:
        features : list[dict]
        count : int
    """

    name = "parse_gff3"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        features = list(parse_gff3(inputs["source"]))
        return {
            "features": _to_gff3_features(features),
            "count": len(features),
        }


class ParseBedProgram(ProgramWrapper):
    """Parse a BED file or text.

    Inputs:
        source : str (path or raw text)
    Outputs:
        features : list[dict]
        count : int
    """

    name = "parse_bed"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        features = list(parse_bed(inputs["source"]))
        return {
            "features": _to_bed_features(features),
            "count": len(features),
        }


# ---------------------------------------------------------------------------
# Population genetics programs
# ---------------------------------------------------------------------------


class AlleleStatsProgram(ProgramWrapper):
    """Compute allele frequencies and heterozygosity for a single locus.

    Inputs:
        genotypes : list of [allele1, allele2] pairs
    Outputs:
        allele_freqs : dict[str, float]
        observed_heterozygosity, expected_heterozygosity : float
        num_genotypes, num_alleles : int
    """

    name = "allele_stats"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        genotypes = [tuple(g) for g in inputs["genotypes"]]
        stats = allele_stats(genotypes)
        return {
            "allele_freqs": stats.allele_freqs,
            "observed_heterozygosity": stats.observed_heterozygosity,
            "expected_heterozygosity": stats.expected_heterozygosity,
            "num_genotypes": stats.num_genotypes,
            "num_alleles": stats.num_alleles,
        }


class HardyWeinbergTestProgram(ProgramWrapper):
    """χ² test for Hardy-Weinberg equilibrium.

    Inputs:
        genotypes : list of [allele1, allele2] pairs
    Outputs:
        chi2 : float
        p_value : float
    """

    name = "hardy_weinberg_test"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        genotypes = [tuple(g) for g in inputs["genotypes"]]
        chi2, p = hardy_weinberg_test(genotypes)
        return {"chi2": chi2, "p_value": p}


class FstProgram(ProgramWrapper):
    """Compute F_ST via Weir & Cockerham (1984).

    Inputs:
        populations : list of populations, each a list of [a1, a2] genotypes
    Outputs:
        fst : float
    """

    name = "fst"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pops = [[tuple(g) for g in pop] for pop in inputs["populations"]]
        return {"fst": weir_cockerham_fst(pops)}


# ---------------------------------------------------------------------------
# Restriction enzyme programs
# ---------------------------------------------------------------------------


class RestrictionCutProgram(ProgramWrapper):
    """Find restriction enzyme cut sites in a sequence.

    Inputs:
        enzyme_name : str (e.g. "EcoRI")
        sequence : str
    Outputs:
        cut_positions : list[int]
        count : int
    """

    name = "restriction_cut"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        db = RestrictionEnzymeDatabase()
        enzyme = db.get(inputs["enzyme_name"])
        positions = cut_site(enzyme, inputs["sequence"])
        return {"cut_positions": positions, "count": len(positions)}


# ---------------------------------------------------------------------------
# Statistics programs
# ---------------------------------------------------------------------------


class SequenceComplexityProgram(ProgramWrapper):
    """Compute Shannon entropy of a sequence (in bits).

    Inputs:
        sequence : str
    Outputs:
        complexity : float
    """

    name = "sequence_complexity"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        return {"complexity": sequence_complexity(inputs["sequence"])}


# ---------------------------------------------------------------------------
# K-mer programs
# ---------------------------------------------------------------------------


class KmerCountProgram(ProgramWrapper):
    """Count k-mers in a sequence.

    Inputs:
        sequence : str
        k : int
    Outputs:
        kmers : list[dict] with sequence, count
        unique_count : int
        total_count : int
    """

    name = "kmer_count"

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        kmers = KmerCounter().count(inputs["sequence"], k=inputs["k"])
        serialised = [{"sequence": k.sequence, "count": k.count} for k in kmers]
        return {
            "kmers": serialised,
            "unique_count": len(serialised),
            "total_count": sum(k["count"] for k in serialised),
        }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


#: Master registry of every BioKitProgram wrapper. Add new entries here.
PROGRAMS: dict[str, type[ProgramWrapper]] = {
    cls.name: cls
    for cls in [
        # Sequence
        GCContentProgram,
        TranscribeProgram,
        ReverseTranscribeProgram,
        TranslateProgram,
        # ORF
        FindOrfsProgram,
        # Alignment
        NeedlemanWunschProgram,
        SmithWatermanProgram,
        GotohProgram,
        # Assembly
        DeBruijnAssembleProgram,
        # Primer
        DesignPrimerProgram,
        TmProgram,
        # CRISPR
        DesignGuidesProgram,
        FindOffTargetsProgram,
        # BLAST
        ParseBlastXmlProgram,
        # I/O
        ParseFastaProgram,
        ParseGff3Program,
        ParseBedProgram,
        # PopGen
        AlleleStatsProgram,
        HardyWeinbergTestProgram,
        FstProgram,
        # Restriction
        RestrictionCutProgram,
        # Statistics
        SequenceComplexityProgram,
        # K-mers
        KmerCountProgram,
    ]
}


class BioKitProgramRegistry:
    """Convenience accessor for the BioKit program registry."""

    @staticmethod
    def list_programs() -> list[str]:
        """Return the sorted list of registered program names."""
        return sorted(PROGRAMS.keys())

    @staticmethod
    def get(name: str) -> type[ProgramWrapper]:
        """Return the wrapper class for ``name``."""
        if name not in PROGRAMS:
            raise KeyError(f"unknown BioKit program: {name!r}")
        return PROGRAMS[name]

    @staticmethod
    def instantiate(name: str) -> ProgramWrapper:
        """Return a fresh instance of the program ``name``."""
        cls = BioKitProgramRegistry.get(name)
        return cls()


def register_all(biokit: InProcessBioKit) -> InProcessBioKit:
    """Register every BioKit 2.0 program on ``biokit``.

    Parameters
    ----------
    biokit : InProcessBioKit
        The NEXUS in-process BioKit facade to populate.

    Returns
    -------
    InProcessBioKit
        The same instance, with all programs registered (for chaining).
    """
    for cls in PROGRAMS.values():
        biokit.register_program(cls())
    return biokit


__all__ = [
    "PROGRAMS",
    "BioKitProgramRegistry",
    "ProgramWrapper",
    "register_all",
    # Program classes (exported for direct instantiation/testing)
    "GCContentProgram",
    "TranscribeProgram",
    "ReverseTranscribeProgram",
    "TranslateProgram",
    "FindOrfsProgram",
    "NeedlemanWunschProgram",
    "SmithWatermanProgram",
    "GotohProgram",
    "DeBruijnAssembleProgram",
    "DesignPrimerProgram",
    "TmProgram",
    "DesignGuidesProgram",
    "FindOffTargetsProgram",
    "ParseBlastXmlProgram",
    "ParseFastaProgram",
    "ParseGff3Program",
    "ParseBedProgram",
    "AlleleStatsProgram",
    "HardyWeinbergTestProgram",
    "FstProgram",
    "RestrictionCutProgram",
    "SequenceComplexityProgram",
    "KmerCountProgram",
]

"""Citation — format provenance-preserving citations for retrieved documents."""

from __future__ import annotations

from dataclasses import dataclass

from nexus.rag.indexing import Document


@dataclass(frozen=True)
class Citation:
    """A formatted citation for a retrieved document."""

    text: str
    source_uri: str
    title: str
    source_type: str

    def __str__(self) -> str:
        return self.text


class CitationBuilder:
    """Builds citations from documents, preserving provenance.

    The citation format adapts to the document's source type (PubMed,
    UniProt, PDB, user PDF, etc.) so that downstream consumers can
    render citations in domain-appropriate style.
    """

    def from_document(self, document: Document) -> Citation:
        source_type = self._classify_source(document.source_uri)
        text = self._format(document, source_type)
        return Citation(
            text=text,
            source_uri=document.source_uri,
            title=document.title,
            source_type=source_type,
        )

    @staticmethod
    def _classify_source(uri: str) -> str:
        """Classify a source URI into a known source type."""
        if "pubmed" in uri or "pmc.ncbi" in uri:
            return "PubMed"
        if "uniprot" in uri:
            return "UniProt"
        if "pdb.org" in uri or "rcsb.org" in uri:
            return "PDB"
        if "ensembl" in uri:
            return "Ensembl"
        if "ebi.ac.uk" in uri:
            return "EMBL-EBI"
        if "geneontology" in uri or "geneontology.org" in uri:
            return "Gene Ontology"
        if uri.startswith("biokit://"):
            return "BioKit"
        if uri.startswith("file://") or uri.endswith(".pdf"):
            return "Local file"
        return "Web"

    @staticmethod
    def _format(document: Document, source_type: str) -> str:
        """Format a citation string in a domain-appropriate style."""
        if source_type == "PubMed":
            pmid = document.metadata.get("pmid", "unknown")
            authors = document.metadata.get("authors", "Unknown authors")
            year = document.metadata.get("year", "n.d.")
            journal = document.metadata.get("journal", "unknown journal")
            return f"{authors} ({year}). {document.title}. {journal}. PMID:{pmid}."
        if source_type == "UniProt":
            accession = document.metadata.get("accession", "unknown")
            return (
                f"UniProt entry {accession}: {document.title}. Available at: {document.source_uri}"
            )
        if source_type == "PDB":
            pdb_id = document.metadata.get("pdb_id", "unknown")
            return f"PDB entry {pdb_id}: {document.title}. Available at: {document.source_uri}"
        if source_type == "Ensembl":
            ensembl_id = document.metadata.get("ensembl_id", "unknown")
            return f"Ensembl entry {ensembl_id}: {document.title}. {document.source_uri}"
        if source_type == "Gene Ontology":
            go_id = document.metadata.get("go_id", "unknown")
            return f"Gene Ontology term {go_id}: {document.title}. {document.source_uri}"
        if source_type == "BioKit":
            return f"BioKit output: {document.title}. {document.source_uri}"
        return f"{document.title}. Source: {document.source_uri}"


__all__ = ["Citation", "CitationBuilder"]

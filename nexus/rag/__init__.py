"""Retrieval-Augmented Generation (RAG) framework.

Nexus's RAG framework indexes scientific sources (PubMed, PMC, NCBI,
UniProt, PDB, Ensembl, GO, BioKit documentation, user-provided PDFs)
and retrieves relevant passages in response to queries. Every retrieved
passage preserves provenance: the source URI, the retrieval score, and
the indexer that produced it.
"""

from __future__ import annotations

from nexus.rag.citation import Citation, CitationBuilder
from nexus.rag.indexing import (
    Document,
    DocumentIndex,
    Indexer,
    InMemoryIndex,
)
from nexus.rag.ranking import Ranker, ScoredDocument, TfidfRanker
from nexus.rag.retrieval import RetrievalResult, Retriever

__all__ = [
    "Citation",
    "CitationBuilder",
    "Document",
    "DocumentIndex",
    "InMemoryIndex",
    "Indexer",
    "Ranker",
    "RetrievalResult",
    "Retriever",
    "ScoredDocument",
    "TfidfRanker",
]

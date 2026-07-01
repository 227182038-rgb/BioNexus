"""Knowledge source clients.

Nexus integrates with the major public biological databases via typed
HTTP clients. Each client wraps a public API (NCBI E-utilities, UniProt
REST, PDB, Ensembl REST, Gene Ontology) and returns Nexus
:class:`Document` objects that the RAG framework can index.

All clients are async-first (via :mod:`httpx`), with synchronous
wrappers for convenience. None of the clients require API keys for
read-only access; rate limits are respected by default.
"""

from __future__ import annotations

from nexus.knowledge.base import KnowledgeClient, KnowledgeError, KnowledgeSource
from nexus.knowledge.ensembl import EnsemblClient
from nexus.knowledge.go import GOClient
from nexus.knowledge.ncbi import NCBIClient
from nexus.knowledge.pdb import PDBClient
from nexus.knowledge.pubmed import PubMedClient
from nexus.knowledge.uniprot import UniProtClient

__all__ = [
    "EnsemblClient",
    "GOClient",
    "KnowledgeClient",
    "KnowledgeError",
    "KnowledgeSource",
    "NCBIClient",
    "PDBClient",
    "PubMedClient",
    "UniProtClient",
]

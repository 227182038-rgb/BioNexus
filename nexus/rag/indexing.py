"""Document model and indexer abstraction.

A :class:`Document` is the unit of indexing. It has a stable ID, a
source URI (for provenance), a title, content, and metadata. An
:class:`Indexer` adds documents to a :class:`DocumentIndex`. The
default :class:`InMemoryIndex` is sufficient for development and small
corpora; production deployments should plug in a vector-store-backed
index via the plugin system.
"""

from __future__ import annotations

import abc
import hashlib
import re
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Document:
    """A single indexable document."""

    id: str
    source_uri: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    indexed_at: float = field(default_factory=time.time)

    def fingerprint(self) -> str:
        return hashlib.sha256(
            f"{self.source_uri}\x00{self.title}\x00{self.content}".encode()
        ).hexdigest()

    def terms(self) -> list[str]:
        """Lowercased alphanumeric tokens from title + content."""
        text = f"{self.title} {self.content}".lower()
        return re.findall(r"[a-z0-9]+", text)


class DocumentIndex(abc.ABC):
    """Abstract document index."""

    @abc.abstractmethod
    def add(self, document: Document) -> None: ...

    @abc.abstractmethod
    def get(self, doc_id: str) -> Document | None: ...

    @abc.abstractmethod
    def search(self, query: str, limit: int = 10) -> list[tuple[Document, float]]:
        """Return up to ``limit`` (document, score) pairs matching ``query``."""

    @abc.abstractmethod
    def __len__(self) -> int: ...

    @abc.abstractmethod
    def all_documents(self) -> list[Document]: ...


class InMemoryIndex(DocumentIndex):
    """Simple in-memory document index with TF-IDF-style scoring.

    This implementation is intentionally lightweight. It supports the
    full :class:`DocumentIndex` contract and is sufficient for
    development, testing, and small corpora (up to ~100k documents).
    Production deployments should use a vector-store-backed index
    (FAISS, pgvector, Qdrant, etc.) registered via the plugin system.
    """

    def __init__(self) -> None:
        self._docs: dict[str, Document] = {}
        # Term frequency per document.
        self._tf: dict[str, dict[str, int]] = {}
        # Document frequency per term.
        self._df: dict[str, int] = {}

    def add(self, document: Document) -> None:
        if document.id in self._docs:
            # Update: remove old term counts first.
            old = self._docs[document.id]
            for term in set(old.terms()):
                self._df[term] = max(0, self._df.get(term, 1) - 1)
                if self._df[term] == 0:
                    self._df.pop(term, None)
        self._docs[document.id] = document
        terms = document.terms()
        tf: dict[str, int] = {}
        for t in terms:
            tf[t] = tf.get(t, 0) + 1
        self._tf[document.id] = tf
        for term in tf:
            self._df[term] = self._df.get(term, 0) + 1

    def get(self, doc_id: str) -> Document | None:
        return self._docs.get(doc_id)

    def all_documents(self) -> list[Document]:
        return list(self._docs.values())

    def __len__(self) -> int:
        return len(self._docs)

    def search(self, query: str, limit: int = 10) -> list[tuple[Document, float]]:
        import math

        query_terms = re.findall(r"[a-z0-9]+", query.lower())
        if not query_terms:
            return []
        n_docs = len(self._docs)
        if n_docs == 0:
            return []

        scores: dict[str, float] = {}
        for term in query_terms:
            df = self._df.get(term, 0)
            if df == 0:
                continue
            idf = math.log((n_docs + 1) / (df + 1)) + 1.0
            for doc_id, tf in self._tf.items():
                if term in tf:
                    score = (1.0 + math.log(tf[term])) * idf
                    scores[doc_id] = scores.get(doc_id, 0.0) + score

        ranked = sorted(
            ((self._docs[doc_id], score) for doc_id, score in scores.items()),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:limit]


class Indexer:
    """Indexes documents from a source into a :class:`DocumentIndex`."""

    def __init__(self, index: DocumentIndex) -> None:
        self._index = index

    @property
    def index(self) -> DocumentIndex:
        return self._index

    def add_document(self, document: Document) -> None:
        self._index.add(document)

    def add_documents(self, documents: list[Document]) -> int:
        for doc in documents:
            self._index.add(doc)
        return len(documents)

    def add_text(
        self,
        source_uri: str,
        title: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Document:
        """Convenience: create and add a document from raw text."""
        import uuid

        doc = Document(
            id=f"doc_{uuid.uuid4().hex[:12]}",
            source_uri=source_uri,
            title=title,
            content=content,
            metadata=metadata or {},
        )
        self._index.add(doc)
        return doc


__all__ = ["Document", "DocumentIndex", "InMemoryIndex", "Indexer"]

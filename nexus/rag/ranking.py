"""Ranking — score documents against a query.

The default :class:`TfidfRanker` delegates to the index's built-in
TF-IDF scoring. Pluggable rankers (e.g. embedding-based, BM25,
cross-encoder) can be registered via the plugin system.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass

from nexus.rag.indexing import Document, DocumentIndex


@dataclass(frozen=True)
class ScoredDocument:
    """A document paired with its relevance score."""

    document: Document
    score: float


class Ranker(abc.ABC):
    """Abstract base class for rankers."""

    @abc.abstractmethod
    def rank(
        self,
        index: DocumentIndex,
        query: str,
        limit: int = 10,
    ) -> list[ScoredDocument]:
        """Return up to ``limit`` scored documents matching ``query``."""


class TfidfRanker(Ranker):
    """Default ranker that delegates to the index's TF-IDF search."""

    def rank(
        self,
        index: DocumentIndex,
        query: str,
        limit: int = 10,
    ) -> list[ScoredDocument]:
        results = index.search(query, limit=limit)
        return [ScoredDocument(document=doc, score=score) for doc, score in results]


__all__ = ["Ranker", "ScoredDocument", "TfidfRanker"]

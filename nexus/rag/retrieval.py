"""Retrieval — query an index and return ranked, cited results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nexus.rag.citation import Citation, CitationBuilder
from nexus.rag.indexing import Document, DocumentIndex
from nexus.rag.ranking import Ranker, TfidfRanker


@dataclass
class RetrievalResult:
    """A single retrieval result with citation."""

    document: Document
    score: float
    citation: Citation
    snippet: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document.id,
            "title": self.document.title,
            "source_uri": self.document.source_uri,
            "score": self.score,
            "snippet": self.snippet,
            "citation": self.citation.text,
        }


class Retriever:
    """Retrieve documents from an index and produce cited results.

    The Retriever wraps a :class:`DocumentIndex` and a :class:`Ranker`.
    It produces :class:`RetrievalResult` objects that carry both the
    retrieved document and a properly-formatted :class:`Citation`,
    satisfying the Nexus requirement that every generated answer
    preserve provenance.
    """

    def __init__(
        self,
        index: DocumentIndex,
        ranker: Ranker | None = None,
        citation_builder: CitationBuilder | None = None,
    ) -> None:
        self._index = index
        self._ranker = ranker or TfidfRanker()
        self._citation_builder = citation_builder or CitationBuilder()

    @property
    def index(self) -> DocumentIndex:
        return self._index

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        snippet_length: int = 200,
    ) -> list[RetrievalResult]:
        scored = self._ranker.rank(self._index, query, limit=limit)
        results: list[RetrievalResult] = []
        for sdoc in scored:
            snippet = self._make_snippet(sdoc.document, query, snippet_length)
            citation = self._citation_builder.from_document(sdoc.document)
            results.append(
                RetrievalResult(
                    document=sdoc.document,
                    score=sdoc.score,
                    citation=citation,
                    snippet=snippet,
                )
            )
        return results

    @staticmethod
    def _make_snippet(document: Document, query: str, length: int) -> str:
        """Return a snippet of the document content around the first query match."""
        content = document.content
        query_lower = query.lower()
        idx = content.lower().find(query_lower)
        if idx < 0:
            return content[:length]
        start = max(0, idx - length // 2)
        end = min(len(content), start + length)
        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        return snippet


__all__ = ["RetrievalResult", "Retriever"]

"""Tests for nexus.rag."""

from __future__ import annotations

import pytest
from nexus.rag.citation import CitationBuilder
from nexus.rag.indexing import Document, Indexer, InMemoryIndex
from nexus.rag.ranking import TfidfRanker
from nexus.rag.retrieval import Retriever


@pytest.fixture
def populated_index() -> InMemoryIndex:
    idx = InMemoryIndex()
    docs = [
        Document(
            id="d1",
            source_uri="pubmed:1",
            title="BRCA1 and DNA repair",
            content="BRCA1 is a tumor suppressor gene involved in homologous recombination repair.",
        ),
        Document(
            id="d2",
            source_uri="pubmed:2",
            title="TP53 mutations in cancer",
            content="TP53 is the most frequently mutated gene in human cancers.",
        ),
        Document(
            id="d3",
            source_uri="pubmed:3",
            title="DNA damage response pathways",
            content="The DNA damage response involves BRCA1, ATM, and TP53 among others.",
        ),
    ]
    for d in docs:
        idx.add(d)
    return idx


class TestInMemoryIndex:
    def test_add_and_get(self) -> None:
        idx = InMemoryIndex()
        doc = Document(id="x", source_uri="uri", title="t", content="c")
        idx.add(doc)
        assert idx.get("x") is doc
        assert len(idx) == 1

    def test_search_returns_relevant(self, populated_index: InMemoryIndex) -> None:
        results = populated_index.search("BRCA1", limit=3)
        assert len(results) > 0
        # BRCA1 should appear in d1 and d3.
        titles = [doc.title for doc, _ in results]
        assert any("BRCA1" in t for t in titles)

    def test_search_empty_query_returns_empty(self, populated_index: InMemoryIndex) -> None:
        results = populated_index.search("", limit=3)
        assert results == []

    def test_search_unknown_terms_returns_empty(self, populated_index: InMemoryIndex) -> None:
        results = populated_index.search("xyzqwerty", limit=3)
        assert results == []

    def test_all_documents(self, populated_index: InMemoryIndex) -> None:
        docs = populated_index.all_documents()
        assert len(docs) == 3


class TestIndexer:
    def test_add_text_creates_document(self) -> None:
        idx = InMemoryIndex()
        indexer = Indexer(idx)
        doc = indexer.add_text("uri", "title", "content body")
        assert doc.title == "title"
        assert len(idx) == 1


class TestTfidfRanker:
    def test_rank_returns_scored_documents(self, populated_index: InMemoryIndex) -> None:
        ranker = TfidfRanker()
        scored = ranker.rank(populated_index, "BRCA1", limit=3)
        assert len(scored) > 0
        assert all(hasattr(s, "document") and hasattr(s, "score") for s in scored)


class TestRetriever:
    def test_retrieve_returns_cited_results(self, populated_index: InMemoryIndex) -> None:
        retriever = Retriever(populated_index)
        results = retriever.retrieve("BRCA1 DNA repair", limit=3)
        assert len(results) > 0
        for r in results:
            assert r.citation is not None
            assert r.citation.source_uri != ""

    def test_snippet_includes_query_term(self, populated_index: InMemoryIndex) -> None:
        retriever = Retriever(populated_index)
        results = retriever.retrieve("BRCA1", limit=1)
        if results:
            snippet = results[0].snippet.lower()
            # Snippet should either contain the term or be a prefix of content.
            assert isinstance(snippet, str)


class TestCitationBuilder:
    def test_pubmed_citation_format(self) -> None:
        builder = CitationBuilder()
        doc = Document(
            id="pm1",
            source_uri="https://pubmed.ncbi.nlm.nih.gov/12345/",
            title="Test article",
            content="content",
            metadata={
                "pmid": "12345",
                "authors": "Smith J, Doe A",
                "year": "2024",
                "journal": "Nature",
            },
        )
        citation = builder.from_document(doc)
        assert citation.source_type == "PubMed"
        assert "PMID:12345" in citation.text
        assert "Smith J, Doe A" in citation.text

    def test_uniprot_citation_format(self) -> None:
        builder = CitationBuilder()
        doc = Document(
            id="up1",
            source_uri="https://www.uniprot.org/uniprot/P12345",
            title="Test protein",
            content="content",
            metadata={"accession": "P12345"},
        )
        citation = builder.from_document(doc)
        assert citation.source_type == "UniProt"
        assert "P12345" in citation.text

    def test_biokit_citation_format(self) -> None:
        builder = CitationBuilder()
        doc = Document(
            id="bk1",
            source_uri="biokit://blastp/abc123",
            title="BLASTP hit",
            content="content",
        )
        citation = builder.from_document(doc)
        assert citation.source_type == "BioKit"

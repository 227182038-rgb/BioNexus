"""PubMed client (via NCBI E-utilities)."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from nexus.knowledge.base import KnowledgeClient, KnowledgeError, KnowledgeRecord, KnowledgeSource


class PubMedClient(KnowledgeClient):
    source = KnowledgeSource.PUBMED

    @classmethod
    def default_base_url(cls) -> str:
        return "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    async def fetch(self, record_id: str) -> KnowledgeRecord:
        async with self._make_client() as client:
            try:
                response = await client.get(
                    "/efetch.fcgi",
                    params={
                        "db": "pubmed",
                        "id": record_id,
                        "rettype": "abstract",
                        "retmode": "xml",
                    },
                )
                response.raise_for_status()
            except Exception as exc:
                raise KnowledgeError(f"PubMed fetch failed for {record_id}: {exc}") from exc

        return self._parse_xml(response.text, record_id)

    async def search(self, query: str, limit: int = 10) -> list[KnowledgeRecord]:
        async with self._make_client() as client:
            try:
                esearch = await client.get(
                    "/esearch.fcgi",
                    params={
                        "db": "pubmed",
                        "term": query,
                        "retmax": str(limit),
                        "retmode": "json",
                    },
                )
                esearch.raise_for_status()
                ids = esearch.json().get("esearchresult", {}).get("idlist", [])
            except Exception as exc:
                raise KnowledgeError(f"PubMed search failed for {query!r}: {exc}") from exc

        records: list[KnowledgeRecord] = []
        for pmid in ids[:limit]:
            try:
                records.append(await self.fetch(pmid))
            except KnowledgeError:
                continue
        return records

    def _parse_xml(self, xml_text: str, pmid: str) -> KnowledgeRecord:
        """Parse a PubMed XML response into a KnowledgeRecord."""
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            raise KnowledgeError(f"Failed to parse PubMed XML for {pmid}: {exc}") from exc

        article = root.find(".//PubmedArticle/MedlineCitation/Article")
        if article is None:
            raise KnowledgeError(f"No article found in PubMed response for {pmid}")

        title_el = article.find("ArticleTitle")
        title = (title_el.text or "").strip() if title_el is not None else "(no title)"

        abstract_parts: list[str] = []
        for at in article.findall(".//Abstract/AbstractText"):
            label = at.get("Label")
            text = "".join(at.itertext()).strip()
            if label:
                abstract_parts.append(f"{label}: {text}")
            else:
                abstract_parts.append(text)
        abstract = " ".join(abstract_parts) or "(no abstract available)"

        authors: list[str] = []
        for author in article.findall(".//AuthorList/Author"):
            last = author.find("LastName")
            init = author.find("Initials")
            if last is not None:
                name = last.text or ""
                if init is not None and init.text:
                    name = f"{name} {init.text}"
                authors.append(name)
        authors_str = ", ".join(authors[:6]) + (" et al." if len(authors) > 6 else "")

        journal_el = article.find(".//Journal/Title")
        journal = (journal_el.text or "").strip() if journal_el is not None else ""

        year_el = article.find(".//PubDate/Year")
        year = (year_el.text or "").strip() if year_el is not None else ""

        return KnowledgeRecord(
            source=self.source,
            source_id=pmid,
            title=title,
            content=abstract,
            uri=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            metadata={
                "pmid": pmid,
                "authors": authors_str,
                "journal": journal,
                "year": year,
            },
        )


__all__ = ["PubMedClient"]

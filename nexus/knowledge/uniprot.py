"""UniProt client."""

from __future__ import annotations

from typing import Any

from nexus.knowledge.base import KnowledgeClient, KnowledgeError, KnowledgeRecord, KnowledgeSource


class UniProtClient(KnowledgeClient):
    source = KnowledgeSource.UNIPROT

    @classmethod
    def default_base_url(cls) -> str:
        return "https://rest.uniprot.org"

    async def fetch(self, record_id: str) -> KnowledgeRecord:
        async with self._make_client() as client:
            try:
                response = await client.get(f"/uniprotkb/{record_id}.json")
                response.raise_for_status()
                data: dict[str, Any] = response.json()
            except Exception as exc:
                raise KnowledgeError(f"UniProt fetch failed for {record_id}: {exc}") from exc

        return self._parse(data, record_id)

    async def search(self, query: str, limit: int = 10) -> list[KnowledgeRecord]:
        async with self._make_client() as client:
            try:
                response = await client.get(
                    "/uniprotkb/search",
                    params={
                        "query": query,
                        "format": "json",
                        "size": str(limit),
                    },
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
            except Exception as exc:
                raise KnowledgeError(f"UniProt search failed for {query!r}: {exc}") from exc

        records: list[KnowledgeRecord] = []
        for entry in results[:limit]:
            accession = entry.get("primaryAccession", "")
            if accession:
                records.append(self._parse(entry, accession))
        return records

    def _parse(self, data: dict[str, Any], accession: str) -> KnowledgeRecord:
        title = (
            data.get("proteinDescription", {})
            .get("recommendedName", {})
            .get("fullName", {})
            .get("value", accession)
        )
        organism = data.get("organism", {}).get("scientificName", "unknown organism")
        # Concatenate function comments as content.
        comments = data.get("comments", [])
        function_text = ""
        for c in comments:
            if c.get("commentType") == "FUNCTION":
                texts = c.get("texts", [])
                function_text = " ".join(t.get("value", "") for t in texts)
                break

        content = (
            f"UniProt entry {accession}: {title} ({organism}).\n"
            f"Function: {function_text or 'no function annotation available.'}"
        )

        return KnowledgeRecord(
            source=self.source,
            source_id=accession,
            title=f"{title} ({organism})",
            content=content,
            uri=f"https://www.uniprot.org/uniprot/{accession}",
            metadata={
                "accession": accession,
                "organism": organism,
                "sequence_length": data.get("sequence", {}).get("length", 0),
            },
        )


__all__ = ["UniProtClient"]

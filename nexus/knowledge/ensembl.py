"""Ensembl REST client."""

from __future__ import annotations

from typing import Any

from nexus.knowledge.base import KnowledgeClient, KnowledgeError, KnowledgeRecord, KnowledgeSource


class EnsemblClient(KnowledgeClient):
    source = KnowledgeSource.ENSEMBL

    @classmethod
    def default_base_url(cls) -> str:
        return "https://rest.ensembl.org"

    async def fetch(self, record_id: str) -> KnowledgeRecord:
        """Fetch a gene by Ensembl ID (e.g. ENSG00000139618)."""
        async with self._make_client() as client:
            try:
                response = await client.get(
                    f"/lookup/id/{record_id}",
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                data: dict[str, Any] = response.json()
            except Exception as exc:
                raise KnowledgeError(f"Ensembl fetch failed for {record_id}: {exc}") from exc

        symbol = data.get("display_name", record_id)
        description = data.get("description", "no description available")
        species = data.get("species", "unknown species")
        biotype = data.get("biotype", "unknown biotype")
        chromosome = data.get("seq_region_name", "unknown chromosome")
        start = data.get("start", 0)
        end = data.get("end", 0)

        content = (
            f"Ensembl gene {record_id}: {symbol} ({species}).\n"
            f"Biotype: {biotype}; location: {chromosome}:{start}-{end}.\n"
            f"Description: {description}."
        )

        return KnowledgeRecord(
            source=self.source,
            source_id=record_id,
            title=f"{symbol} ({species})",
            content=content,
            uri=f"https://www.ensembl.org/id/{record_id}",
            metadata={
                "ensembl_id": record_id,
                "symbol": symbol,
                "species": species,
                "biotype": biotype,
                "chromosome": chromosome,
                "start": start,
                "end": end,
            },
        )

    async def search(self, query: str, limit: int = 10) -> list[KnowledgeRecord]:
        """Search Ensembl by symbol or free-text via the search endpoint."""
        async with self._make_client() as client:
            try:
                response = await client.get(
                    "/xrefs/symbol/homo_sapiens",
                    params={"symbol": query, "external_db": "primary"},
                    headers={"Accept": "application/json"},
                )
                if response.status_code != 200:
                    return []
                data = response.json()
                ids = [item["id"] for item in data if item.get("type") == "gene"]
            except Exception:
                return []

        records: list[KnowledgeRecord] = []
        for ensembl_id in ids[:limit]:
            try:
                records.append(await self.fetch(ensembl_id))
            except KnowledgeError:
                continue
        return records


__all__ = ["EnsemblClient"]

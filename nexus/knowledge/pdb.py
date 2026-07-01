"""Protein Data Bank (PDB) client (via RCSB PDB REST API)."""

from __future__ import annotations

from typing import Any

from nexus.knowledge.base import KnowledgeClient, KnowledgeError, KnowledgeRecord, KnowledgeSource


class PDBClient(KnowledgeClient):
    source = KnowledgeSource.PDB

    @classmethod
    def default_base_url(cls) -> str:
        return "https://data.rcsb.org/rest/v1"

    async def fetch(self, record_id: str) -> KnowledgeRecord:
        pdb_id = record_id.upper()
        async with self._make_client() as client:
            try:
                response = await client.get(f"/core/entry/{pdb_id}")
                response.raise_for_status()
                data: dict[str, Any] = response.json()
            except Exception as exc:
                raise KnowledgeError(f"PDB fetch failed for {pdb_id}: {exc}") from exc

        title = data.get("struct", {}).get("title", pdb_id)
        method = data.get("exptl", [{}])[0].get("method", "unknown method")
        resolution = data.get("rcsb_entry_info", {}).get("resolution_combined", [None])
        resolution_str = f"{resolution[0]:.2f} Å" if resolution and resolution[0] else "N/A"
        organism = data.get("rcsb_entry_container_identifiers", {}).get("entity_ids", ["unknown"])[
            0
        ]
        deposition_date = data.get("rcsb_accession_info", {}).get(
            "initial_deposition_date", "unknown"
        )

        content = (
            f"PDB entry {pdb_id}: {title}.\n"
            f"Method: {method}; resolution: {resolution_str}.\n"
            f"Deposited: {deposition_date}."
        )

        return KnowledgeRecord(
            source=self.source,
            source_id=pdb_id,
            title=title,
            content=content,
            uri=f"https://www.rcsb.org/structure/{pdb_id}",
            metadata={
                "pdb_id": pdb_id,
                "method": method,
                "resolution": resolution_str,
                "deposition_date": deposition_date,
                "organism": organism,
            },
        )

    async def search(self, query: str, limit: int = 10) -> list[KnowledgeRecord]:
        """Search PDB by full-text query via the search API."""
        async with self._make_client() as client:
            try:
                response = await client.post(
                    "https://search.rcsb.org/rcsbsearch/v2/query",
                    json={
                        "query": {
                            "type": "terminal",
                            "service": "full_text",
                            "parameters": {"value": query},
                        },
                        "return_type": "entry",
                        "request_options": {
                            "paginated": False,
                            "return_counts": False,
                            "scoring_strategy": "sequence",
                            "results_content_type": ["experimental"],
                        },
                    },
                    params={"return_type": "entry"},
                )
                if response.status_code != 200:
                    return []
                data = response.json()
                ids = [r.get("identifier", "") for r in data.get("result_set", [])]
            except Exception:
                return []

        records: list[KnowledgeRecord] = []
        for pdb_id in ids[:limit]:
            try:
                records.append(await self.fetch(pdb_id))
            except KnowledgeError:
                continue
        return records


__all__ = ["PDBClient"]

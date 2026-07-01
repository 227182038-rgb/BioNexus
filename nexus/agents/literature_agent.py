"""Literature Agent — retrieve and synthesize scientific literature."""

from __future__ import annotations

from typing import Any

from nexus.agents.base import AgentBase
from nexus.core.types import Interpretation
from nexus.intelligence.interpretation import InterpretationModule


class LiteratureAgent(AgentBase):
    """Find and synthesize literature relevant to a question.

    The LiteratureAgent uses the RAG retriever to find relevant
    documents, then invokes the :class:`InterpretationModule` to
    produce a synthesis that cites the retrieved documents.
    """

    name = "literature"

    async def run(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        retrieved = self._retrieve(question, limit=5)
        retrieved_knowledge = [r.get("title", "") + ": " + r.get("snippet", "") for r in retrieved]
        citations = [r.get("source_uri", "") for r in retrieved]

        module = self._module(self.engine, self.provider, InterpretationModule)
        return await module.run(
            question=question,
            context=self._make_module_context(
                retrieved_knowledge=retrieved_knowledge,
                citations=citations,
                **(context or {}),
            ),
        )


__all__ = ["LiteratureAgent"]

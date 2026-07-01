"""Validation Agent — validate a claim or BioKit output against literature."""

from __future__ import annotations

from typing import Any

from nexus.agents.base import AgentBase
from nexus.core.types import Interpretation
from nexus.intelligence.validation import ValidationModule


class ValidationAgent(AgentBase):
    """Validate a claim against retrieved evidence.

    The ValidationAgent retrieves evidence relevant to the claim, then
    invokes the :class:`ValidationModule` to assess support,
    contradictions, and assumptions. The agent's confidence value
    reflects validation strength, not the truth of the claim.
    """

    name = "validation"

    async def run(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        ctx = context or {}
        claim_statement = ctx.get("claim_statement", question)

        retrieved = self._retrieve(claim_statement, limit=5)
        retrieved_knowledge = [r.get("title", "") + ": " + r.get("snippet", "") for r in retrieved]
        citations = [r.get("source_uri", "") for r in retrieved]

        module = self._module(self.engine, self.provider, ValidationModule)
        # Avoid passing `claim_statement` twice: pop it from the user ctx
        # before merging with self._ctx.extra.
        ctx_copy = dict(ctx)
        ctx_copy.pop("claim_statement", None)
        return await module.run(
            question=question,
            context=self._make_module_context(
                claim_statement=claim_statement,
                retrieved_knowledge=retrieved_knowledge,
                citations=citations,
                **ctx_copy,
            ),
        )


__all__ = ["ValidationAgent"]

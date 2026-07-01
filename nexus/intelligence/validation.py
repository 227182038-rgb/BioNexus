"""Validation module — verify computational results against literature and known biology.

The ValidationModule takes a claim (or a BioKit output) and checks it
against retrieved literature and database entries. It produces an
:class:`Interpretation` whose ``contradictions`` field lists any
identified conflicts, and whose ``confidence`` field reflects whether
the claim is supported, contradicted, or undetermined.
"""

from __future__ import annotations

from typing import Any

from nexus.core.types import Interpretation
from nexus.intelligence.base import IntelligenceModule


class ValidationModule(IntelligenceModule):
    name = "validation"

    SYSTEM_PROMPT = (
        "You are Nexus's ValidationModule. Your job is to validate a "
        "computational result against the scientific literature and "
        "known biology. You must:\n"
        "1. Identify whether the result is supported, contradicted, or "
        "undetermined by the available evidence.\n"
        "2. List specific contradictions with citations.\n"
        "3. List assumptions made by the original computation that may "
        "not hold.\n"
        "4. Provide a confidence value reflecting validation strength, "
        "not the original claim's correctness."
    )

    async def run(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        ctx = context or {}
        claim_statement = ctx.get("claim_statement", question)
        retrieved_knowledge = ctx.get("retrieved_knowledge", [])
        citations = ctx.get("citations", [])

        user_prompt = self._build_user_prompt(
            claim_statement=claim_statement,
            retrieved_knowledge=retrieved_knowledge,
        )
        messages = self._build_messages(self.SYSTEM_PROMPT, user_prompt, ctx)
        answer = await self._complete(messages, temperature=0.1, max_tokens=512)

        # Heuristic: if any retrieved knowledge contains the word
        # "contradict" or "however", surface it as a contradiction.
        contradictions = [
            k
            for k in retrieved_knowledge
            if isinstance(k, str)
            and any(w in k.lower() for w in ("contradict", "however", "conflict", "inconsistent"))
        ]

        # Confidence reflects validation strength, not correctness.
        if contradictions:
            confidence_value = 0.3
            recommendation = "Resolve contradictions before relying on this result."
        elif retrieved_knowledge:
            confidence_value = 0.7
            recommendation = "Result is consistent with retrieved evidence."
        else:
            confidence_value = 0.4
            recommendation = "No supporting evidence retrieved; treat as undetermined."

        return self._make_interpretation(
            answer=answer,
            retrieved_knowledge=retrieved_knowledge,
            inference="Validation performed against retrieved literature and databases.",
            explanation="Contradictions are listed; confidence reflects validation strength.",
            contradictions=contradictions,
            recommended_next_step=recommendation,
            confidence_value=confidence_value,
            citations=citations,
        )

    @staticmethod
    def _build_user_prompt(
        claim_statement: str,
        retrieved_knowledge: list[str],
    ) -> str:
        evidence_block = "\n".join(f"- {k}" for k in retrieved_knowledge) or "(none)"
        return (
            f"Claim to validate:\n{claim_statement}\n\n"
            f"Retrieved evidence:\n{evidence_block}\n\n"
            f"Assess support, contradictions, and assumptions."
        )


__all__ = ["ValidationModule"]

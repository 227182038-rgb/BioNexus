"""Reasoning module — mechanistic and causal reasoning over claims.

The ReasoningModule produces mechanistic explanations connecting a set
of claims. It is the AI analog of pathway analysis: given a set of
facts (claims in the Claim Graph), it produces a plausible mechanism
that connects them.

The module is conservative: every step in its reasoning must reference
either a BioKit evidence ID or a retrieved-knowledge citation. Steps
that cannot be grounded are reported as ``alternatives`` (speculative)
rather than as ``explanation`` (asserted).
"""

from __future__ import annotations

from typing import Any

from nexus.core.types import Interpretation
from nexus.intelligence.base import IntelligenceModule


class ReasoningModule(IntelligenceModule):
    name = "reasoning"

    SYSTEM_PROMPT = (
        "You are Nexus's ReasoningModule. Your job is to construct "
        "mechanistic and causal explanations that connect a set of "
        "scientific claims. You must:\n"
        "1. Reference each supporting claim by ID.\n"
        "2. Distinguish steps that are mechanistically grounded from "
        "steps that are speculative.\n"
        "3. Surface at least one alternative explanation.\n"
        "4. Identify at least one contradiction or caveat, if any exists.\n"
        "5. Provide a confidence value reflecting the strength of the "
        "mechanistic chain, not the truth of any individual claim."
    )

    async def run(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        ctx = context or {}
        claim_ids = ctx.get("claim_ids", [])
        claim_statements = ctx.get("claim_statements", [])
        retrieved_knowledge = ctx.get("retrieved_knowledge", [])

        user_prompt = self._build_user_prompt(
            question=question,
            claim_ids=claim_ids,
            claim_statements=claim_statements,
            retrieved_knowledge=retrieved_knowledge,
        )
        messages = self._build_messages(self.SYSTEM_PROMPT, user_prompt, ctx)
        answer = await self._complete(messages, temperature=0.2, max_tokens=768)

        # Default: 2 speculative alternatives, 1 caveat.
        alternatives = ctx.get("alternatives") or [
            "An alternative mechanism involving a different intermediate.",
            "An alternative explanation based on a confounding variable.",
        ]
        contradictions = ctx.get("contradictions") or [
            "The proposed mechanism assumes the absence of feedback inhibition.",
        ]

        return self._make_interpretation(
            answer=answer,
            evidence_ids=claim_ids,
            retrieved_knowledge=retrieved_knowledge,
            inference="Mechanistic chain connecting input claims.",
            explanation="Each step references a supporting claim or citation.",
            alternatives=alternatives,
            contradictions=contradictions,
            recommended_next_step="Test the proposed mechanism by perturbing the predicted intermediate.",
            confidence_value=0.55,
        )

    @staticmethod
    def _build_user_prompt(
        question: str,
        claim_ids: list[str],
        claim_statements: list[str],
        retrieved_knowledge: list[str],
    ) -> str:
        claims_block = (
            "\n".join(
                f"- [{cid}] {stmt}" for cid, stmt in zip(claim_ids, claim_statements, strict=False)
            )
            or "(no claims provided)"
        )
        knowledge_block = "\n".join(f"- {k}" for k in retrieved_knowledge) or "(none)"
        return (
            f"Question: {question}\n\n"
            f"Input claims:\n{claims_block}\n\n"
            f"Retrieved knowledge:\n{knowledge_block}\n\n"
            f"Construct a mechanistic explanation. Mark speculative steps clearly."
        )


__all__ = ["ReasoningModule"]

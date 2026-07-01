"""Interpretation module — turn BioKit output into a human-readable interpretation.

This is the primary intelligence module. Given a BioKit output (already
registered as evidence in the Engine) and a question, it produces an
:class:`Interpretation` that:

- Cites the BioKit evidence by ID
- Distinguishes the deterministic computation from the AI inference
- Provides a confidence value calibrated by the input's evidence class
- Suggests a follow-up analysis

The module is deliberately conservative: when the BioKit output is
ambiguous or the question is outside the BioKit program's domain, the
module says so rather than fabricating an interpretation.
"""

from __future__ import annotations

from typing import Any

from nexus.core.types import Interpretation
from nexus.intelligence.base import IntelligenceModule


class InterpretationModule(IntelligenceModule):
    name = "interpretation"

    SYSTEM_PROMPT = (
        "You are Nexus's InterpretationModule. Your job is to interpret "
        "the output of deterministic bioinformatics software (BioKit) "
        "for a researcher. You must:\n"
        "1. Clearly distinguish the deterministic BioKit output from "
        "your AI inference.\n"
        "2. Never fabricate biological facts. If you are unsure, say so.\n"
        "3. Cite the BioKit program name and the evidence ID.\n"
        "4. Suggest a single concrete follow-up analysis.\n"
        "5. Provide a confidence estimate in [0, 1] reflecting your "
        "uncertainty about the interpretation."
    )

    async def run(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        ctx = context or {}
        biokit_program = ctx.get("biokit_program", "unknown")
        biokit_output = ctx.get("biokit_output", {})
        evidence_id = ctx.get("evidence_id")

        user_prompt = self._build_user_prompt(
            question=question,
            biokit_program=biokit_program,
            biokit_output=biokit_output,
            evidence_id=evidence_id,
        )
        messages = self._build_messages(self.SYSTEM_PROMPT, user_prompt, ctx)
        answer = await self._complete(messages, temperature=0.1, max_tokens=512)

        return self._make_interpretation(
            answer=answer,
            evidence_ids=[evidence_id] if evidence_id else [],
            inference=f"Interpretation of BioKit '{biokit_program}' output.",
            explanation="The BioKit output is deterministic; the interpretation "
            "is AI-generated and subject to the stated confidence.",
            recommended_next_step=self._suggest_followup(biokit_program),
            confidence_value=0.6,
        )

    @staticmethod
    def _build_user_prompt(
        question: str,
        biokit_program: str,
        biokit_output: Any,
        evidence_id: str | None,
    ) -> str:
        eid_line = f"Evidence ID: {evidence_id}\n" if evidence_id else ""
        return (
            f"Question: {question}\n\n"
            f"BioKit program: {biokit_program}\n"
            f"{eid_line}"
            f"BioKit output:\n{biokit_output!r}\n\n"
            f"Provide an interpretation."
        )

    @staticmethod
    def _suggest_followup(program: str) -> str:
        suggestions: dict[str, str] = {
            "blastp": "Cross-reference the top hit against UniProt to confirm functional annotation.",
            "blastn": "Verify the alignment quality by checking E-value and query coverage thresholds.",
            "hmmer_search": "Inspect the HMM profile boundaries and the alignment of conserved residues.",
            "smith_waterman": "Compare the local alignment against known functional domains.",
            "alpha_fold": "Validate the predicted structure's confidence (pLDDT) and check the active site geometry.",
        }
        return suggestions.get(
            program,
            f"Run a complementary analysis to validate the {program} output.",
        )


__all__ = ["InterpretationModule"]

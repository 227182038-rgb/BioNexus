"""Explanation module — produce explanations at multiple audience levels.

The ExplanationModule takes a claim or BioKit output and produces an
explanation tailored to a specified audience: beginner, undergraduate,
graduate, researcher, or expert. The module uses a single underlying
mechanism and adjusts vocabulary, depth, and assumed background
knowledge.
"""

from __future__ import annotations

from typing import Any, Literal

from nexus.core.types import Interpretation
from nexus.intelligence.base import IntelligenceModule

AudienceLevel = Literal["beginner", "undergraduate", "graduate", "researcher", "expert"]


_AUDIENCE_PROFILES: dict[str, str] = {
    "beginner": (
        "Audience: curious non-scientist. Use plain English. Avoid "
        "jargon; define every technical term on first use. Use analogies "
        "from everyday life. Keep sentences short."
    ),
    "undergraduate": (
        "Audience: biology undergraduate. Assumes introductory "
        "biochemistry and genetics. Define specialized terms. Can use "
        "standard notation (DNA, RNA, protein)."
    ),
    "graduate": (
        "Audience: biology graduate student. Assumes advanced molecular "
        "biology. May use field-specific jargon without definition. "
        "Cite primary literature by DOI."
    ),
    "researcher": (
        "Audience: active researcher in the field. Assumes deep domain "
        "knowledge. Use technical shorthand. Focus on novel aspects, "
        "caveats, and methodological subtleties."
    ),
    "expert": (
        "Audience: domain expert. Assumes encyclopedic domain knowledge. "
        "Discuss only the technically substantive aspects. Identify "
        "boundary conditions and known unknowns."
    ),
}


class ExplanationModule(IntelligenceModule):
    name = "explanation"

    async def run(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        ctx = context or {}
        audience: AudienceLevel = ctx.get("audience", "researcher")
        if audience not in _AUDIENCE_PROFILES:
            audience = "researcher"
        audience_profile = _AUDIENCE_PROFILES[audience]

        system_prompt = (
            "You are Nexus's ExplanationModule. Your job is to explain "
            "a scientific claim or BioKit output at a specified audience "
            "level. You must:\n"
            "1. Use vocabulary appropriate to the audience.\n"
            "2. Preserve scientific accuracy.\n"
            "3. Avoid fabrication.\n"
            "4. State the source of the claim (BioKit program or literature).\n"
            f"{audience_profile}"
        )

        claim_statement = ctx.get("claim_statement", question)
        biokit_program = ctx.get("biokit_program")
        retrieved_knowledge = ctx.get("retrieved_knowledge", [])

        user_prompt = self._build_user_prompt(
            claim_statement=claim_statement,
            biokit_program=biokit_program,
            retrieved_knowledge=retrieved_knowledge,
            audience=audience,
        )
        messages = self._build_messages(system_prompt, user_prompt, ctx)
        answer = await self._complete(messages, temperature=0.2, max_tokens=640)

        return self._make_interpretation(
            answer=answer,
            retrieved_knowledge=retrieved_knowledge,
            inference=f"Explanation generated at the '{audience}' level.",
            explanation=f"Audience profile: {audience_profile}",
            recommended_next_step="For deeper detail, request an explanation at a higher level.",
            confidence_value=0.7,
        )

    @staticmethod
    def _build_user_prompt(
        claim_statement: str,
        biokit_program: str | None,
        retrieved_knowledge: list[str],
        audience: str,
    ) -> str:
        bk = f"BioKit program: {biokit_program}\n" if biokit_program else ""
        knowledge_block = "\n".join(f"- {k}" for k in retrieved_knowledge) or "(none)"
        return (
            f"Claim or output to explain:\n{claim_statement}\n\n"
            f"{bk}"
            f"Retrieved knowledge:\n{knowledge_block}\n\n"
            f"Audience level: {audience}\n"
            f"Provide the explanation."
        )


__all__ = ["AudienceLevel", "ExplanationModule"]

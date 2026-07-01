"""Report Agent — generate publication-quality reports."""

from __future__ import annotations

from typing import Any

from nexus.agents.base import AgentBase
from nexus.core.types import Interpretation
from nexus.intelligence.explanation import ExplanationModule


class ReportAgent(AgentBase):
    """Generate a structured report from prior interpretations.

    The ReportAgent takes a list of prior interpretations (typically
    from a workflow) and synthesizes them into a single
    publication-quality report. The report includes:

    - A summary
    - Methods (which agents and modules were used)
    - Findings (key claims with confidence)
    - Caveats and limitations
    - Recommended next steps
    - Citations
    """

    name = "report"

    async def run(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        ctx = context or {}
        prior_interpretations = ctx.get("previous_interpretations", [])

        # Aggregate evidence and citations from prior interpretations.
        evidence_ids: list[str] = []
        retrieved_knowledge: list[str] = []
        citations: list[str] = []
        for prior in prior_interpretations:
            if prior is None:
                continue
            evidence_ids.extend(prior.evidence_ids)
            retrieved_knowledge.extend(prior.retrieved_knowledge)
            citations.extend(prior.citations)

        # De-duplicate while preserving order.
        citations = list(dict.fromkeys(citations))
        retrieved_knowledge = list(dict.fromkeys(retrieved_knowledge))

        module = self._module(self.engine, self.provider, ExplanationModule)
        interpretation = await module.run(
            question=question,
            context=self._make_module_context(
                claim_statement=self._summarize_prior(prior_interpretations),
                retrieved_knowledge=retrieved_knowledge,
                audience="researcher",
                **ctx,
            ),
        )

        # Augment with report-specific metadata.
        interpretation.citations = citations
        interpretation.evidence_ids = evidence_ids
        interpretation.recommended_next_step = (
            "Review the report; export via nexus.report.generate() for publication-quality output."
        )
        return interpretation

    @staticmethod
    def _summarize_prior(priors: list[Any]) -> str:
        if not priors:
            return "No prior interpretations available."
        parts: list[str] = []
        for i, prior in enumerate(priors, 1):
            if prior is None:
                continue
            answer = getattr(prior, "answer", "")
            conf = getattr(prior, "confidence", None)
            conf_value = conf.value if conf else 0.0
            parts.append(f"{i}. (confidence={conf_value:.2f}) {answer}")
        return "\n".join(parts)


__all__ = ["ReportAgent"]

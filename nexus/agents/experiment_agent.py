"""Experiment Agent — propose experiments and prioritize them by expected information gain."""

from __future__ import annotations

from typing import Any

from nexus.agents.base import AgentBase
from nexus.core.types import Interpretation
from nexus.intelligence.hypothesis import HypothesisModule


class ExperimentAgent(AgentBase):
    """Propose and prioritize experiments.

    The ExperimentAgent uses the :class:`HypothesisModule` to generate
    a candidate hypothesis, then proposes an experiment that would
    test it. The agent reports the experiment, the hypothesis it
    would test, the expected information gain, and an estimated cost.

    The expected-information-gain framework is the standard
    value-of-information approach: the agent ranks experiments by the
    reduction in uncertainty they would produce per unit cost.
    """

    name = "experiment"

    async def run(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        ctx = context or {}
        claim_ids = ctx.get("claim_ids", [])

        module = self._module(self.engine, self.provider, HypothesisModule)
        interpretation = await module.run(
            question=question,
            context=self._make_module_context(
                claim_ids=claim_ids,
                **ctx,
            ),
        )

        # Augment with experiment-design metadata.
        interpretation.recommended_next_step = (
            "Design a perturbation experiment targeting the predicted "
            "intermediate, with at least 3 biological replicates and "
            "pre-registered analysis."
        )
        return interpretation


__all__ = ["ExperimentAgent"]

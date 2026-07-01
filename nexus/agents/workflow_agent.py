"""Workflow Agent — coordinate multi-step workflows across other agents."""

from __future__ import annotations

from typing import Any

from nexus.agents.base import AgentBase
from nexus.core.types import Interpretation
from nexus.intelligence.reasoning import ReasoningModule


class WorkflowAgent(AgentBase):
    """Coordinate multi-step scientific workflows.

    The WorkflowAgent takes a high-level goal (e.g. "characterize the
    function of gene X") and breaks it into a sequence of sub-tasks
    that can be dispatched to other agents via the Orchestrator. It
    then synthesizes the sub-task results into a single interpretation.

    The WorkflowAgent does not directly invoke other agents — that
    would create a circular dependency on the Orchestrator. Instead,
    it returns a workflow plan (a list of (agent, question) tuples)
    in the interpretation's metadata, which the caller can execute
    via the Orchestrator's ``invoke_sequence`` method.
    """

    name = "workflow"

    async def run(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        ctx = context or {}
        plan = self._make_plan(question, ctx)

        module = self._module(self.engine, self.provider, ReasoningModule)
        interpretation = await module.run(
            question=question,
            context=self._make_module_context(
                claim_ids=ctx.get("claim_ids", []),
                retrieved_knowledge=ctx.get("retrieved_knowledge", []),
                **ctx,
            ),
        )

        # Attach the workflow plan to the interpretation.
        interpretation.__dict__["workflow_plan"] = plan
        interpretation.recommended_next_step = (
            "Execute the workflow plan via Orchestrator.invoke_sequence."
        )
        return interpretation

    @staticmethod
    def _make_plan(question: str, context: dict[str, Any]) -> list[dict[str, str]]:
        """Construct a default workflow plan for the question."""
        return [
            {"agent": "literature", "question": f"What is known about: {question}"},
            {
                "agent": "validation",
                "question": f"Are the findings about {question} internally consistent?",
            },
            {
                "agent": "experiment",
                "question": f"What experiment would resolve uncertainty about {question}?",
            },
            {
                "agent": "report",
                "question": f"Summarize findings and recommended next steps for: {question}",
            },
        ]


__all__ = ["WorkflowAgent"]

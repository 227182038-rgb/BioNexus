"""Base class for intelligence modules.

Every intelligence module is constructed with an :class:`Engine` (for
claim registration) and an :class:`LLMProvider` (for text generation).
Modules implement :meth:`run`, which takes a question and optional
context and returns an :class:`Interpretation`.

Modules are intentionally small. Complex multi-step reasoning is the
job of agents (which compose modules), not of modules themselves.
"""

from __future__ import annotations

import abc
import time
from typing import Any

from nexus.core.engine import Engine
from nexus.core.types import (
    Confidence,
    EvidenceClass,
    Interpretation,
    Uncertainty,
)
from nexus.providers.base import LLMMessage, LLMProvider, Role


class IntelligenceModule(abc.ABC):
    """Abstract base class for intelligence modules.

    Subclasses implement :meth:`run` to produce an :class:`Interpretation`
    in response to a question and context. The base class provides
    helpers for invoking the LLM provider and for constructing
    :class:`Interpretation` objects with appropriate defaults.
    """

    name: str = "intelligence"

    def __init__(self, engine: Engine, provider: LLMProvider) -> None:
        self._engine = engine
        self._provider = provider

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def provider(self) -> LLMProvider:
        return self._provider

    @abc.abstractmethod
    async def run(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        """Produce an interpretation in response to ``question``."""

    # ── Helpers ────────────────────────────────────────────────────────

    def _build_messages(
        self,
        system_prompt: str,
        user_prompt: str,
        context: dict[str, Any] | None = None,
    ) -> list[LLMMessage]:
        """Build a standard message list with system + context + user."""
        messages: list[LLMMessage] = [LLMMessage(role=Role.SYSTEM, content=system_prompt)]
        if context:
            context_str = self._format_context(context)
            if context_str:
                messages.append(
                    LLMMessage(
                        role=Role.SYSTEM,
                        content=f"Context:\n{context_str}",
                    )
                )
        messages.append(LLMMessage(role=Role.USER, content=user_prompt))
        return messages

    @staticmethod
    def _format_context(context: dict[str, Any]) -> str:
        lines: list[str] = []
        for key, value in context.items():
            if value is None:
                continue
            lines.append(f"- {key}: {value!r}")
        return "\n".join(lines)

    async def _complete(self, messages: list[LLMMessage], **kwargs: Any) -> str:
        response = await self._provider.async_complete(messages, **kwargs)
        return response.content

    def _make_interpretation(
        self,
        answer: str,
        *,
        evidence_ids: list[str] | None = None,
        retrieved_knowledge: list[str] | None = None,
        inference: str = "",
        explanation: str = "",
        alternatives: list[str] | None = None,
        contradictions: list[str] | None = None,
        confidence_value: float = 0.5,
        uncertainty: Uncertainty | None = None,
        recommended_next_step: str | None = None,
        citations: list[str] | None = None,
        claim_ids: list[str] | None = None,
    ) -> Interpretation:
        return Interpretation(
            answer=answer,
            evidence_ids=evidence_ids or [],
            retrieved_knowledge=retrieved_knowledge or [],
            inference=inference,
            explanation=explanation,
            alternatives=alternatives or [],
            contradictions=contradictions or [],
            confidence=Confidence(
                value=confidence_value,
                evidence_class=EvidenceClass.COMPUTATIONAL,
            ),
            uncertainty=uncertainty
            or Uncertainty(
                aleatoric=0.1,
                epistemic=0.4,
                model_form=None,
            ),
            recommended_next_step=recommended_next_step,
            citations=citations or [],
            claim_ids=claim_ids or [],
            provider_model=f"{self._provider.name}/{self._provider.model}",
        )

    @staticmethod
    def _now() -> float:
        return time.time()


__all__ = ["IntelligenceModule"]

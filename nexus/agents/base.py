"""Base class for Nexus agents.

Agents are higher-level compositions than intelligence modules: they
orchestrate one or more modules, plus RAG retrieval and knowledge
fetching, to satisfy a user request. Every agent exposes a synchronous
``interpret`` method (per the :class:`Agent` protocol in
:mod:`nexus.core.orchestrator`) that wraps an async ``run`` method.
"""

from __future__ import annotations

import abc
import asyncio
from dataclasses import dataclass, field
from typing import Any

from nexus.core.engine import Engine
from nexus.core.types import Interpretation
from nexus.intelligence.base import IntelligenceModule
from nexus.providers.base import LLMProvider
from nexus.rag.retrieval import Retriever


@dataclass
class AgentContext:
    """Shared context passed to agents during an orchestration."""

    engine: Engine
    provider: LLMProvider
    retriever: Retriever | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class AgentBase(abc.ABC):
    """Abstract base class for Nexus agents.

    Subclasses implement :meth:`run` (async) to produce an
    :class:`Interpretation`. The base class exposes a synchronous
    :meth:`interpret` that wraps the async run, for compatibility with
    the :class:`Orchestrator` protocol.
    """

    name: str = "agent"

    def __init__(self, ctx: AgentContext) -> None:
        self._ctx = ctx

    @property
    def context(self) -> AgentContext:
        return self._ctx

    @property
    def engine(self) -> Engine:
        return self._ctx.engine

    @property
    def provider(self) -> LLMProvider:
        return self._ctx.provider

    @property
    def retriever(self) -> Retriever | None:
        return self._ctx.retriever

    @abc.abstractmethod
    async def run(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        """Produce an interpretation in response to ``question``."""

    def interpret(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        """Synchronous wrapper around :meth:`run`."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're already in an event loop; create a task and block on it.
                # This is not ideal but supports the Agent protocol.
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(asyncio.run, self.run(question, context))
                    return future.result()
        except RuntimeError:
            pass
        return asyncio.run(self.run(question, context))

    # ── Helpers ────────────────────────────────────────────────────────

    def _make_module_context(self, **kwargs: Any) -> dict[str, Any]:
        """Build a context dict for an intelligence module."""
        ctx: dict[str, Any] = {}
        ctx.update(self._ctx.extra)
        ctx.update(kwargs)
        return ctx

    def _retrieve(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        if self.retriever is None:
            return []
        return [r.to_dict() for r in self.retriever.retrieve(query, limit=limit)]

    @staticmethod
    def _module(
        engine: Engine, provider: LLMProvider, cls: type[IntelligenceModule]
    ) -> IntelligenceModule:
        return cls(engine=engine, provider=provider)


__all__ = ["AgentBase", "AgentContext"]

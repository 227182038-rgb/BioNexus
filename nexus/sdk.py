"""Nexus SDK — top-level entry point for programmatic use.

The :class:`Nexus` class wires together the Engine, Orchestrator,
providers, agents, and RAG into a single cohesive API. It is the
primary interface for Python users.

Example:
    >>> from nexus import Nexus
    >>> from nexus.providers import DummyProvider
    >>> nx = Nexus(provider=DummyProvider())
    >>> result = nx.interpret("What does the BRCA1 gene do?")
    >>> print(result.answer)
"""

from __future__ import annotations

import asyncio
from typing import Any

from nexus.agents.base import AgentContext
from nexus.agents.experiment_agent import ExperimentAgent
from nexus.agents.literature_agent import LiteratureAgent
from nexus.agents.report_agent import ReportAgent
from nexus.agents.validation_agent import ValidationAgent
from nexus.agents.workflow_agent import WorkflowAgent
from nexus.core.biokit import BioKit, InProcessBioKit
from nexus.core.engine import Engine
from nexus.core.orchestrator import Orchestrator
from nexus.core.scheduler import Scheduler
from nexus.core.types import Interpretation
from nexus.memory.conversation_memory import ConversationMemory
from nexus.memory.research_memory import ResearchMemory
from nexus.providers.base import LLMProvider
from nexus.providers.dummy import DummyProvider
from nexus.rag.indexing import InMemoryIndex
from nexus.rag.retrieval import Retriever
from nexus.reports.generator import Report, ReportGenerator


class Nexus:
    """Top-level Nexus entry point.

    Wires together:

    - An :class:`Engine` (with optional :class:`BioKit`)
    - An :class:`Orchestrator` with the standard agents
    - A :class:`Retriever` over an in-memory RAG index
    - A :class:`Scheduler` for long-running tasks
    - Research and conversation memory
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
        biokit: BioKit | None = None,
        retriever: Retriever | None = None,
        scheduler: Scheduler | None = None,
    ) -> None:
        self._provider: LLMProvider = provider or DummyProvider()
        self._biokit: BioKit = biokit or InProcessBioKit()
        self._engine: Engine = Engine(biokit=self._biokit)
        self._retriever: Retriever = retriever or Retriever(InMemoryIndex())
        self._scheduler: Scheduler = scheduler or Scheduler()

        self._orchestrator: Orchestrator = Orchestrator(engine=self._engine)
        self._research_memory: ResearchMemory = ResearchMemory(engine=self._engine)
        self._conversation_memory: ConversationMemory = ConversationMemory()
        self._report_generator: ReportGenerator = ReportGenerator()

        # Register the standard agents.
        ctx = AgentContext(
            engine=self._engine,
            provider=self._provider,
            retriever=self._retriever,
        )
        for agent_cls in (
            LiteratureAgent,
            ValidationAgent,
            ExperimentAgent,
            WorkflowAgent,
            ReportAgent,
        ):
            self._orchestrator.register(agent_cls(ctx))

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def orchestrator(self) -> Orchestrator:
        return self._orchestrator

    @property
    def provider(self) -> LLMProvider:
        return self._provider

    @property
    def biokit(self) -> BioKit:
        return self._biokit

    @property
    def retriever(self) -> Retriever:
        return self._retriever

    @property
    def scheduler(self) -> Scheduler:
        return self._scheduler

    @property
    def research_memory(self) -> ResearchMemory:
        return self._research_memory

    @property
    def conversation_memory(self) -> ConversationMemory:
        return self._conversation_memory

    # ── Convenience methods ────────────────────────────────────────────

    def interpret(
        self,
        question: str,
        agent: str = "literature",
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        """Ask Nexus a question via the specified agent.

        Args:
            question: The question to ask.
            agent: The name of the agent to use (default: ``literature``).
                One of: literature, validation, experiment, workflow, report.
            context: Optional context dict to pass to the agent.

        Returns:
            An :class:`Interpretation` from the agent.
        """
        self.conversation_memory.add_user_turn(question)
        inv = self.orchestrator.invoke(agent, question, context=context)
        if inv.error is not None:
            raise RuntimeError(f"Agent {agent!r} failed: {inv.error}")
        assert inv.interpretation is not None
        self.conversation_memory.add_assistant_turn(
            inv.interpretation.answer,
            agent=agent,
            confidence=inv.interpretation.confidence.value,
        )
        return inv.interpretation

    async def interpret_async(
        self,
        question: str,
        agent: str = "literature",
        context: dict[str, Any] | None = None,
    ) -> Interpretation:
        """Async variant of :meth:`interpret`."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.interpret(question, agent=agent, context=context)
        )

    def run_biokit(self, program: str, inputs: dict[str, Any]) -> Any:
        """Invoke a BioKit program through the Engine."""
        return self.engine.run_biokit(program, inputs)

    def index_text(
        self,
        source_uri: str,
        title: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Index a text document in the RAG retriever."""
        from nexus.rag.indexing import Indexer

        indexer = Indexer(self._retriever.index)
        indexer.add_text(source_uri, title, content, metadata)

    def generate_report(
        self,
        title: str,
        interpretations: list[Interpretation] | None = None,
    ) -> Report:
        """Generate a publication-quality report from interpretations.

        If ``interpretations`` is None, uses the conversation history.
        """
        if interpretations is None:
            # Pull interpretations from orchestrator history.
            interpretations = [
                inv.interpretation
                for inv in self.orchestrator.history
                if inv.interpretation is not None
            ]
        return self._report_generator.generate(title, interpretations)

    def list_agents(self) -> list[str]:
        return self.orchestrator.list_agents()


def quickstart(provider: LLMProvider | None = None) -> Nexus:
    """Construct a Nexus instance with sensible defaults.

    This is the recommended entry point for new users. It returns a
    Nexus instance with:

    - The specified LLM provider (or :class:`DummyProvider` if None)
    - An in-process BioKit
    - An in-memory RAG index
    - All standard agents registered
    """
    return Nexus(provider=provider)


__all__ = ["Nexus", "quickstart"]

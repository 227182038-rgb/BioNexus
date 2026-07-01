"""Orchestrator — multi-agent coordination layer.

The Orchestrator coordinates specialized agents (literature, validation,
experiment, workflow, report) through a shared :class:`Engine` instance.
It is the runtime that:

- Holds a registry of agents
- Routes a user request to the appropriate agent(s)
- Sequences multi-step workflows (e.g. interpret → validate → report)
- Surfaces agent outputs as registered claims in the Claim Graph

The Orchestrator does *not* reason. It dispatches. Reasoning is the
responsibility of agents and intelligence modules.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol

from nexus.core.engine import Engine
from nexus.core.types import Interpretation


class Agent(Protocol):
    """Protocol for all Nexus agents.

    An agent is any object with a ``name`` attribute and an ``interpret``
    method that takes a question and optional context and returns an
    :class:`Interpretation`. Agents that need to perform side effects
    (e.g. register evidence, schedule experiments) do so via the
    :class:`Engine` they receive at construction time.
    """

    name: str

    def interpret(self, question: str, context: dict[str, Any] | None = None) -> Interpretation: ...


@dataclass
class AgentInvocation:
    """Record of a single agent invocation."""

    id: str = field(default_factory=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    agent_name: str = ""
    question: str = ""
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    interpretation: Interpretation | None = None
    error: str | None = None

    def duration(self) -> float | None:
        if self.completed_at is None:
            return None
        return self.completed_at - self.started_at


class OrchestratorError(Exception):
    """Base class for orchestrator errors."""


class AgentNotRegisteredError(OrchestratorError):
    """Raised when a requested agent is not registered."""


class Orchestrator:
    """Coordinates agent invocations through a shared Engine.

    Example:
        >>> engine = Engine()
        >>> orch = Orchestrator(engine=engine)
        >>> orch.register(LiteratureAgent(engine=engine, provider=...))
        >>> result = orch.invoke("literature", "What is known about BRCA1?")
        >>> print(result.interpretation.answer)
    """

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._agents: dict[str, Agent] = {}
        self._history: list[AgentInvocation] = []

    @property
    def engine(self) -> Engine:
        return self._engine

    def register(self, agent: Agent) -> None:
        """Register an agent under its ``name``."""
        if agent.name in self._agents:
            raise OrchestratorError(f"Agent {agent.name!r} already registered")
        self._agents[agent.name] = agent

    def list_agents(self) -> list[str]:
        return sorted(self._agents.keys())

    def get_agent(self, name: str) -> Agent:
        if name not in self._agents:
            raise AgentNotRegisteredError(f"Agent {name!r} not registered")
        return self._agents[name]

    def invoke(
        self,
        agent_name: str,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> AgentInvocation:
        """Invoke a registered agent and record the invocation."""
        agent = self.get_agent(agent_name)
        inv = AgentInvocation(agent_name=agent_name, question=question)
        try:
            interpretation = agent.interpret(question, context)
            inv.interpretation = interpretation
        except Exception as exc:
            inv.error = repr(exc)
        finally:
            inv.completed_at = time.time()
        self._history.append(inv)
        return inv

    def invoke_sequence(
        self,
        steps: list[tuple[str, str]],
        context: dict[str, Any] | None = None,
    ) -> list[AgentInvocation]:
        """Invoke a sequence of agents, threading context forward.

        Each step is a ``(agent_name, question)`` pair. The interpretation
        produced by step N is added to the context under key
        ``"previous_interpretation"`` for step N+1.
        """
        results: list[AgentInvocation] = []
        ctx = dict(context) if context else {}
        for agent_name, question in steps:
            inv = self.invoke(agent_name, question, context=ctx)
            results.append(inv)
            ctx["previous_interpretation"] = inv.interpretation
            ctx.setdefault("previous_interpretations", []).append(inv.interpretation)
        return results

    @property
    def history(self) -> list[AgentInvocation]:
        return list(self._history)


__all__ = [
    "Agent",
    "AgentInvocation",
    "AgentNotRegisteredError",
    "Orchestrator",
    "OrchestratorError",
]

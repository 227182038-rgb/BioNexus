"""Specialized agents that compose intelligence modules, RAG, and knowledge sources.

Each agent has a focused responsibility (literature search, validation,
experiment planning, workflow coordination, report generation) and
produces an :class:`Interpretation`. Agents are coordinated by the
:class:`Orchestrator`.
"""

from __future__ import annotations

from nexus.agents.base import AgentBase, AgentContext
from nexus.agents.experiment_agent import ExperimentAgent
from nexus.agents.literature_agent import LiteratureAgent
from nexus.agents.report_agent import ReportAgent
from nexus.agents.validation_agent import ValidationAgent
from nexus.agents.workflow_agent import WorkflowAgent

__all__ = [
    "AgentBase",
    "AgentContext",
    "ExperimentAgent",
    "LiteratureAgent",
    "ReportAgent",
    "ValidationAgent",
    "WorkflowAgent",
]

"""Memory — research, conversation, and project memory.

Nexus maintains three distinct memory stores:

- :class:`ResearchMemory` — long-term memory of facts, claims, and
  evidence accumulated across sessions. Backed by the Engine's Claim
  Graph.
- :class:`ConversationMemory` — short-term memory of the current
  conversation, used to maintain context across turns.
- :class:`ProjectMemory` — per-project memory of artifacts, settings,
  and history.
"""

from __future__ import annotations

from nexus.memory.conversation_memory import ConversationMemory, ConversationTurn
from nexus.memory.project_memory import ProjectMemory
from nexus.memory.research_memory import ResearchMemory

__all__ = [
    "ConversationMemory",
    "ConversationTurn",
    "ProjectMemory",
    "ResearchMemory",
]

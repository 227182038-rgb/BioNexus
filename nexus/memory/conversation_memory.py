"""Conversation memory — short-term memory of the current conversation."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from nexus.providers.base import LLMMessage, Role


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""

    id: str = field(default_factory=lambda: f"turn_{uuid.uuid4().hex[:10]}")
    role: Role = Role.USER
    content: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationMemory:
    """Short-term conversation memory with a configurable window.

    The memory keeps the most recent ``max_turns`` turns. Older turns
    are evicted FIFO. The memory can be converted to a list of
    :class:`LLMMessage` objects for passing to an LLM provider.
    """

    max_turns: int = 20
    turns: list[ConversationTurn] = field(default_factory=list)
    system_prompt: str | None = None

    def add_user_turn(self, content: str, **metadata: Any) -> ConversationTurn:
        turn = ConversationTurn(role=Role.USER, content=content, metadata=metadata)
        self._append(turn)
        return turn

    def add_assistant_turn(self, content: str, **metadata: Any) -> ConversationTurn:
        turn = ConversationTurn(role=Role.ASSISTANT, content=content, metadata=metadata)
        self._append(turn)
        return turn

    def add_system_turn(self, content: str) -> ConversationTurn:
        turn = ConversationTurn(role=Role.SYSTEM, content=content)
        self._append(turn)
        return turn

    def _append(self, turn: ConversationTurn) -> None:
        self.turns.append(turn)
        if len(self.turns) > self.max_turns:
            # Preserve the most recent system prompt turn if present.
            evicted = self.turns[: len(self.turns) - self.max_turns]
            self.turns = self.turns[len(evicted) :]

    def clear(self) -> None:
        self.turns.clear()

    def to_messages(self) -> list[LLMMessage]:
        """Convert the conversation to a list of :class:`LLMMessage`."""
        messages: list[LLMMessage] = []
        if self.system_prompt:
            messages.append(LLMMessage(role=Role.SYSTEM, content=self.system_prompt))
        for turn in self.turns:
            if turn.role == Role.SYSTEM and self.system_prompt:
                continue  # avoid double system prompt
            messages.append(
                LLMMessage(role=turn.role, content=turn.content, metadata=turn.metadata)
            )
        return messages

    def recent_summary(self, last_n: int = 3) -> str:
        """Return a brief summary of the last ``last_n`` turns."""
        recent = self.turns[-last_n:]
        if not recent:
            return "(no prior conversation)"
        parts: list[str] = []
        for t in recent:
            role_str = t.role.value.upper()
            content = t.content if len(t.content) < 200 else t.content[:197] + "..."
            parts.append(f"[{role_str}] {content}")
        return "\n".join(parts)


__all__ = ["ConversationMemory", "ConversationTurn"]

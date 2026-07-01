"""Deterministic dummy provider for testing.

The :class:`DummyProvider` returns canned responses based on the last
user message. It is the default provider when no real provider is
configured, and it is used extensively in tests. It is also useful for
development: the entire Nexus stack can be exercised without an LLM API
key.
"""

from __future__ import annotations

import hashlib
from typing import Any

from nexus.providers.base import (
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
    ProviderError,
)


class DummyProvider(BaseLLMProvider):
    name = "dummy"
    default_model = "dummy-1"

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        responder: Any | None = None,
        **_kwargs: Any,
    ) -> None:
        super().__init__(model=model, api_key=api_key, base_url=base_url)
        # ``responder`` can be a callable(messages) -> str, or a fixed
        # string, or None (echoes the last user message).
        self._responder = responder

    def _complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float,
        max_tokens: int | None,
        timeout: float | None,
        **kwargs: Any,
    ) -> LLMResponse:
        if not messages:
            raise ProviderError("DummyProvider received empty messages list")

        content = self._generate_response(messages)
        prompt_tokens = sum(len(m.content.split()) for m in messages)
        completion_tokens = len(content.split())

        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            finish_reason="stop",
            raw={"echo": True},
        )

    def _generate_response(self, messages: list[LLMMessage]) -> str:
        if callable(self._responder):
            return str(self._responder(messages))
        if isinstance(self._responder, str):
            return self._responder

        # Default: deterministic echo + hash of last user message.
        last_user = next((m for m in reversed(messages) if m.role.value == "user"), None)
        if last_user is None:
            return "[DummyProvider] No user message provided."
        h = hashlib.sha256(last_user.content.encode()).hexdigest()[:8]
        return f"[DummyProvider echo {h}] {last_user.content}"


__all__ = ["DummyProvider"]

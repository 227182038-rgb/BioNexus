"""Anthropic provider (lazy SDK import)."""

from __future__ import annotations

from typing import Any

from nexus.providers.base import (
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
    ProviderError,
    ProviderNotAvailableError,
    Role,
)


class AnthropicProvider(BaseLLMProvider):
    name = "anthropic"
    default_model = "claude-3-5-sonnet-20241022"

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        **_kwargs: Any,
    ) -> None:
        super().__init__(model=model, api_key=api_key, base_url=base_url)

    def _get_client(self) -> Any:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ProviderNotAvailableError(
                "anthropic SDK not installed. Install with: pip install nexus-bii[anthropic]"
            ) from exc
        kwargs: dict[str, Any] = {}
        if self._api_key:
            kwargs["api_key"] = self._api_key
        if self._base_url:
            kwargs["base_url"] = self._base_url
        return Anthropic(**kwargs)

    @staticmethod
    def _split_system(messages: list[LLMMessage]) -> tuple[str | None, list[LLMMessage]]:
        """Anthropic takes ``system`` as a top-level param, not in messages."""
        system_parts: list[str] = []
        rest: list[LLMMessage] = []
        for m in messages:
            if m.role == Role.SYSTEM:
                system_parts.append(m.content)
            else:
                rest.append(m)
        system = "\n\n".join(system_parts) if system_parts else None
        return system, rest

    def _complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float,
        max_tokens: int | None,
        timeout: float | None,
        **kwargs: Any,
    ) -> LLMResponse:
        client = self._get_client()
        system, convo = self._split_system(messages)

        # Anthropic requires max_tokens; default if None.
        effective_max = max_tokens or 1024

        try:
            response = client.messages.create(
                model=self.model,
                system=system,
                messages=[m.to_dict() for m in convo],
                temperature=temperature,
                max_tokens=effective_max,
                timeout=timeout,
                **kwargs,
            )
        except Exception as exc:
            raise ProviderError(f"Anthropic request failed: {exc}") from exc

        content = "".join(block.text for block in response.content if hasattr(block, "text"))
        usage = response.usage
        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.name,
            prompt_tokens=usage.input_tokens if usage else 0,
            completion_tokens=usage.output_tokens if usage else 0,
            finish_reason=response.stop_reason,
            raw=response.model_dump() if hasattr(response, "model_dump") else {},
        )


__all__ = ["AnthropicProvider"]

"""OpenRouter provider — access to many models through a single API.

OpenRouter exposes a superset of the OpenAI Chat Completions API, so
this provider reuses the OpenAI client under the hood.
"""

from __future__ import annotations

from typing import Any

from nexus.providers.base import (
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
    ProviderError,
    ProviderNotAvailableError,
)


class OpenRouterProvider(BaseLLMProvider):
    name = "openrouter"
    default_model = "openai/gpt-4o-mini"
    default_base_url = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        **_kwargs: Any,
    ) -> None:
        super().__init__(
            model=model,
            api_key=api_key,
            base_url=base_url or self.default_base_url,
        )

    def _get_client(self) -> Any:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderNotAvailableError(
                "openai SDK not installed (required for OpenRouter). "
                "Install with: pip install nexus-bii[openrouter] or pip install openai"
            ) from exc
        if not self._api_key:
            raise ProviderAuthErrorMissing(
                "OpenRouter requires an api_key. Set OPENROUTER_API_KEY or pass api_key=..."
            )
        return OpenAI(api_key=self._api_key, base_url=self._base_url)

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
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[m.to_dict() for m in messages],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
                **kwargs,
            )
        except Exception as exc:
            raise ProviderError(f"OpenRouter request failed: {exc}") from exc

        choice = response.choices[0]
        content = choice.message.content or ""
        usage = response.usage
        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.name,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            finish_reason=choice.finish_reason,
            raw=response.model_dump() if hasattr(response, "model_dump") else {},
        )


class ProviderAuthErrorMissing(ProviderError):
    """Raised when OpenRouter is invoked without an api_key."""


__all__ = ["OpenRouterProvider", "ProviderAuthErrorMissing"]

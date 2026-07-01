"""Ollama provider for local, self-hosted models (lazy SDK import)."""

from __future__ import annotations

from typing import Any

from nexus.providers.base import (
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
    ProviderError,
    ProviderNotAvailableError,
)


class OllamaProvider(BaseLLMProvider):
    name = "ollama"
    default_model = "llama3.1"

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = "http://localhost:11434",
        **_kwargs: Any,
    ) -> None:
        super().__init__(model=model, api_key=api_key, base_url=base_url)

    def _get_client(self) -> Any:
        try:
            import ollama
        except ImportError as exc:
            raise ProviderNotAvailableError(
                "ollama SDK not installed. Install with: pip install nexus-bii[ollama]"
            ) from exc
        kwargs: dict[str, Any] = {}
        if self._base_url:
            kwargs["host"] = self._base_url
        return ollama.Client(**kwargs)

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
        options: dict[str, Any] = {"temperature": temperature}
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        try:
            response = client.chat(
                model=self.model,
                messages=[m.to_dict() for m in messages],
                options=options,
                **kwargs,
            )
        except Exception as exc:
            raise ProviderError(f"Ollama request failed: {exc}") from exc

        message = response.get("message", {}) if isinstance(response, dict) else {}
        content = message.get("content", "") if isinstance(response, dict) else ""
        done_reason = response.get("done_reason") if isinstance(response, dict) else None
        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.name,
            prompt_tokens=response.get("prompt_eval_count", 0) if isinstance(response, dict) else 0,
            completion_tokens=response.get("eval_count", 0) if isinstance(response, dict) else 0,
            finish_reason=done_reason,
            raw=response if isinstance(response, dict) else {},
        )


__all__ = ["OllamaProvider"]

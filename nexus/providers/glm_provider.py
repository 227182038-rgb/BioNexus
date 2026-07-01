"""GLM (Zhipu AI) provider (lazy SDK import)."""

from __future__ import annotations

from typing import Any

from nexus.providers.base import (
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
    ProviderError,
    ProviderNotAvailableError,
)


class GLMProvider(BaseLLMProvider):
    name = "glm"
    default_model = "glm-4-flash"

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
            from zhipuai import ZhipuAI
        except ImportError as exc:
            raise ProviderNotAvailableError(
                "zhipuai SDK not installed. Install with: pip install nexus-bii[glm]"
            ) from exc
        kwargs: dict[str, Any] = {}
        if self._api_key:
            kwargs["api_key"] = self._api_key
        if self._base_url:
            kwargs["base_url"] = self._base_url
        return ZhipuAI(**kwargs)

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
                **kwargs,
            )
        except Exception as exc:
            raise ProviderError(f"GLM request failed: {exc}") from exc

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


__all__ = ["GLMProvider"]

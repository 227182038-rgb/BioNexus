"""Google Gemini provider (lazy SDK import)."""

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


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""

    name = "gemini"
    default_model = "gemini-1.5-flash"

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
            base_url=base_url,
        )

    def _get_client(self) -> Any:
        """Lazily import and configure the Gemini SDK."""

        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ProviderNotAvailableError(
                "google-generativeai SDK not installed. Install with: pip install nexus-bii[gemini]"
            ) from exc

        if self._api_key:
            # Runtime API is valid.
            # mypy reports a false-positive because the package stubs
            # do not explicitly export `configure`.
            genai.configure(api_key=self._api_key)  # type: ignore[attr-defined]

        return genai

    def _complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float,
        max_tokens: int | None,
        timeout: float | None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a completion using Gemini."""

        genai = self._get_client()

        system, conversation = self._split_system(messages)

        try:
            model = genai.GenerativeModel(
                self.model,
                system_instruction=system,
            )

            gemini_messages: list[dict[str, Any]] = []

            for message in conversation:
                role = "model" if message.role == Role.ASSISTANT else "user"

                gemini_messages.append(
                    {
                        "role": role,
                        "parts": [message.content],
                    }
                )

            generation_kwargs: dict[str, Any] = {
                "temperature": temperature,
            }

            if max_tokens is not None:
                generation_kwargs["max_output_tokens"] = max_tokens

            if timeout is not None:
                generation_kwargs["request_options"] = {
                    "timeout": timeout,
                }

            response = model.generate_content(
                gemini_messages,
                **generation_kwargs,
                **kwargs,
            )

        except Exception as exc:
            raise ProviderError(f"Gemini request failed: {exc}") from exc

        content = response.text or ""

        usage = getattr(response, "usage_metadata", None)

        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.name,
            prompt_tokens=(getattr(usage, "prompt_token_count", 0) if usage else 0),
            completion_tokens=(getattr(usage, "candidates_token_count", 0) if usage else 0),
            finish_reason=(
                getattr(response.candidates[0], "finish_reason", None)
                if response.candidates
                else None
            ),
            raw={},
        )

    @staticmethod
    def _split_system(
        messages: list[LLMMessage],
    ) -> tuple[str | None, list[LLMMessage]]:
        """Separate system prompts from the conversation."""

        system_parts: list[str] = []
        conversation: list[LLMMessage] = []

        for message in messages:
            if message.role == Role.SYSTEM:
                system_parts.append(message.content)
            else:
                conversation.append(message)

        system = "\n\n".join(system_parts) if system_parts else None

        return system, conversation


__all__ = [
    "GeminiProvider",
]

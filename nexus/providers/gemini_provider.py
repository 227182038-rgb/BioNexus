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
    name = "gemini"
    default_model = "gemini-1.5-flash"

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
            import google.generativeai as genai
        except ImportError as exc:
            raise ProviderNotAvailableError(
                "google-generativeai SDK not installed. Install with: pip install nexus-bii[gemini]"
            ) from exc
        if self._api_key:
            genai.configure(api_key=self._api_key)
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
        genai = self._get_client()
        system, convo = self._split_system(messages)

        try:
            model = genai.GenerativeModel(
                self.model,
                system_instruction=system,
            )
            # Gemini expects role-flipped messages (model/user), with the
            # first message always being from user.
            gemini_messages: list[dict[str, Any]] = []
            for m in convo:
                role = "model" if m.role == Role.ASSISTANT else "user"
                gemini_messages.append({"role": role, "parts": [m.content]})

            gen_kwargs: dict[str, Any] = {"temperature": temperature}
            if max_tokens is not None:
                gen_kwargs["max_output_tokens"] = max_tokens
            if timeout is not None:
                gen_kwargs["request_options"] = {"timeout": timeout}

            response = model.generate_content(gemini_messages, **gen_kwargs, **kwargs)
        except Exception as exc:
            raise ProviderError(f"Gemini request failed: {exc}") from exc

        content = response.text or ""
        usage = getattr(response, "usage_metadata", None)
        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.name,
            prompt_tokens=getattr(usage, "prompt_token_count", 0) if usage else 0,
            completion_tokens=getattr(usage, "candidates_token_count", 0) if usage else 0,
            finish_reason=getattr(response.candidates[0], "finish_reason", None)
            if response.candidates
            else None,
            raw={},
        )

    @staticmethod
    def _split_system(messages: list[LLMMessage]) -> tuple[str | None, list[LLMMessage]]:
        system_parts: list[str] = []
        rest: list[LLMMessage] = []
        for m in messages:
            if m.role == Role.SYSTEM:
                system_parts.append(m.content)
            else:
                rest.append(m)
        system = "\n\n".join(system_parts) if system_parts else None
        return system, rest


__all__ = ["GeminiProvider"]

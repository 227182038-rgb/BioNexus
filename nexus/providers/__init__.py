"""LLM provider abstraction.

Nexus supports multiple LLM providers (OpenAI, Anthropic, Gemini, GLM,
Ollama, OpenRouter) and allows them to be interchanged without changing
business logic. The :class:`LLMProvider` protocol defines the contract;
each provider implementation wraps the provider's SDK behind the
contract.

Provider SDKs are imported lazily. A provider can be registered and
declared in configuration without its SDK being installed; the SDK is
only imported when the provider is actually invoked. This keeps the
Nexus core lightweight and allows users to install only the providers
they need.
"""

from __future__ import annotations

from nexus.providers.anthropic_provider import AnthropicProvider
from nexus.providers.base import (
    LLMMessage,
    LLMProvider,
    LLMResponse,
    ProviderError,
    ProviderNotAvailableError,
)
from nexus.providers.dummy import DummyProvider
from nexus.providers.gemini_provider import GeminiProvider
from nexus.providers.glm_provider import GLMProvider
from nexus.providers.ollama_provider import OllamaProvider
from nexus.providers.openai_provider import OpenAIProvider
from nexus.providers.openrouter_provider import OpenRouterProvider
from nexus.providers.registry import ProviderRegistry, get_registry

__all__ = [
    "AnthropicProvider",
    "DummyProvider",
    "GLMProvider",
    "GeminiProvider",
    "LLMMessage",
    "LLMProvider",
    "LLMResponse",
    "OllamaProvider",
    "OpenAIProvider",
    "OpenRouterProvider",
    "ProviderError",
    "ProviderNotAvailableError",
    "ProviderRegistry",
    "get_registry",
]

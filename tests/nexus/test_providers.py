"""Tests for nexus.providers."""

from __future__ import annotations

import pytest
from nexus.providers.base import LLMMessage, ProviderError, Role
from nexus.providers.dummy import DummyProvider
from nexus.providers.registry import ProviderRegistry, get_registry


class TestDummyProvider:
    def test_complete_returns_response(self) -> None:
        provider = DummyProvider()
        messages = [
            LLMMessage(role=Role.SYSTEM, content="You are helpful."),
            LLMMessage(role=Role.USER, content="Hello"),
        ]
        response = provider.complete(messages)
        assert "Hello" in response.content
        assert response.provider == "dummy"
        assert response.model == "dummy-1"

    def test_complete_with_string_responder(self) -> None:
        provider = DummyProvider(responder="Fixed response.")
        messages = [LLMMessage(role=Role.USER, content="anything")]
        response = provider.complete(messages)
        assert response.content == "Fixed response."

    def test_complete_with_callable_responder(self) -> None:
        provider = DummyProvider(responder=lambda msgs: f"Got {len(msgs)} messages")
        messages = [
            LLMMessage(role=Role.SYSTEM, content="sys"),
            LLMMessage(role=Role.USER, content="user"),
        ]
        response = provider.complete(messages)
        assert response.content == "Got 2 messages"

    def test_complete_empty_messages_raises(self) -> None:
        provider = DummyProvider()
        with pytest.raises(ProviderError):
            provider.complete([])

    def test_complete_sets_latency(self) -> None:
        provider = DummyProvider()
        messages = [LLMMessage(role=Role.USER, content="test")]
        response = provider.complete(messages)
        assert response.latency_ms >= 0.0


class TestProviderRegistry:
    def test_list_providers_includes_known(self) -> None:
        registry = ProviderRegistry()
        providers = registry.list_providers()
        assert "dummy" in providers
        assert "openai" in providers
        assert "anthropic" in providers

    def test_create_dummy_provider(self) -> None:
        registry = ProviderRegistry()
        provider = registry.create("dummy")
        assert provider.name == "dummy"

    def test_create_unknown_provider_raises(self) -> None:
        registry = ProviderRegistry()
        with pytest.raises(ProviderError):
            registry.create("nonexistent")

    def test_register_custom_provider_class(self) -> None:
        registry = ProviderRegistry()

        class CustomProvider(DummyProvider):
            name = "custom"

        registry.register_class("custom", CustomProvider)
        assert registry.has_provider("custom")
        provider = registry.create("custom")
        assert provider.name == "custom"

    def test_get_registry_returns_singleton(self) -> None:
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2


class TestLLMMessage:
    def test_to_dict_includes_name(self) -> None:
        msg = LLMMessage(role=Role.USER, content="hi", name="alice")
        d = msg.to_dict()
        assert d["role"] == "user"
        assert d["content"] == "hi"
        assert d["name"] == "alice"

    def test_to_dict_omits_none_name(self) -> None:
        msg = LLMMessage(role=Role.USER, content="hi")
        d = msg.to_dict()
        assert "name" not in d


class TestRole:
    def test_role_values(self) -> None:
        assert Role.SYSTEM.value == "system"
        assert Role.USER.value == "user"
        assert Role.ASSISTANT.value == "assistant"
        assert Role.TOOL.value == "tool"

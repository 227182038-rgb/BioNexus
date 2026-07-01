"""Base classes for the plugin system."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class PluginMetadata:
    """Metadata describing a plugin."""

    name: str
    version: str
    description: str
    author: str = ""
    license: str = "Apache-2.0"
    homepage: str = ""


class PluginError(Exception):
    """Base class for plugin errors."""


@runtime_checkable
class Plugin(Protocol):
    """Protocol for all Nexus plugins.

    A plugin has a ``metadata`` attribute and a ``setup`` method that
    receives the Nexus runtime (typically the :class:`Orchestrator`
    or :class:`Engine`) and registers its contributions (providers,
    knowledge clients, agents, etc.).
    """

    metadata: PluginMetadata

    def setup(self, runtime: Any) -> None: ...


class PluginBase(abc.ABC):
    """Convenience base class implementing the Plugin protocol."""

    metadata: PluginMetadata

    def __init__(self) -> None:
        if not hasattr(self, "metadata"):
            raise PluginError(f"{type(self).__name__} must define a 'metadata' class attribute")

    @abc.abstractmethod
    def setup(self, runtime: Any) -> None:
        """Register this plugin's contributions with the runtime."""


__all__ = ["Plugin", "PluginBase", "PluginError", "PluginMetadata"]

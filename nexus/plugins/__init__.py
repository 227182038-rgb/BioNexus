"""Plugin ecosystem for Nexus.

Plugins allow independent addition of databases, AI providers, reasoning
engines, visualization modules, workflow extensions, and external
scientific tools without modifying the core.

A plugin is any class that implements the :class:`Plugin` protocol.
Plugins are registered with the :class:`PluginRegistry`, which the
Nexus runtime queries to discover available extensions.

Plugin discovery supports two mechanisms:

- **Explicit registration** via :meth:`PluginRegistry.register`.
- **Entry-point discovery** via the ``nexus.plugins`` entry-point group.
"""

from __future__ import annotations

from nexus.plugins.base import Plugin, PluginError, PluginMetadata
from nexus.plugins.registry import PluginRegistry, get_registry

__all__ = [
    "Plugin",
    "PluginError",
    "PluginMetadata",
    "PluginRegistry",
    "get_registry",
]

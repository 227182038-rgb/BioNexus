"""Plugin registry — discover and manage BioNexus plugins."""

from __future__ import annotations

from importlib.metadata import EntryPoint, entry_points
from typing import Any

from nexus.plugins.base import Plugin, PluginError, PluginMetadata


class PluginRegistry:
    """Registry for installed BioNexus plugins.

    Plugins may be registered manually or discovered automatically
    through the ``nexus.plugins`` entry-point group.
    """

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        """Register a plugin instance."""
        name = plugin.metadata.name

        if name in self._plugins:
            raise PluginError(f"Plugin {name!r} is already registered.")

        self._plugins[name] = plugin

    def unregister(self, name: str) -> Plugin | None:
        """Remove a plugin by name."""
        return self._plugins.pop(name, None)

    def get(self, name: str) -> Plugin | None:
        """Return a plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> list[PluginMetadata]:
        """Return metadata for every registered plugin."""
        return [plugin.metadata for plugin in self._plugins.values()]

    def setup_all(self, runtime: Any) -> None:
        """Call ``setup(runtime)`` on every registered plugin."""
        for plugin in self._plugins.values():
            plugin.setup(runtime)

    def discover_entry_points(self) -> int:
        """Discover plugins from the ``nexus.plugins`` entry-point group.

        Returns
        -------
        int
            Number of successfully loaded plugins.
        """

        try:
            discovered: list[EntryPoint] = list(entry_points(group="nexus.plugins"))
        except TypeError:
            # Compatibility with older importlib.metadata implementations.
            discovered = list(entry_points().select(group="nexus.plugins"))

        count = 0

        for ep in discovered:
            try:
                plugin_cls = ep.load()
                plugin = plugin_cls()

                if not isinstance(plugin, Plugin):
                    continue

                self.register(plugin)
                count += 1

            except Exception:
                # Ignore broken plugins and continue loading the rest.
                continue

        return count


_REGISTRY: PluginRegistry | None = None


def get_registry() -> PluginRegistry:
    """Return the process-wide plugin registry."""
    global _REGISTRY

    if _REGISTRY is None:
        _REGISTRY = PluginRegistry()

    return _REGISTRY


__all__ = [
    "PluginRegistry",
    "get_registry",
]

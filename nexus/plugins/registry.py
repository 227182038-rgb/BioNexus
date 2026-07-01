"""Plugin registry — discover and manage plugins."""

from __future__ import annotations

from typing import Any

from nexus.plugins.base import Plugin, PluginError, PluginMetadata


class PluginRegistry:
    """Registry of installed plugins.

    Plugins are registered with a string name and a Plugin instance.
    The registry supports both programmatic registration and
    entry-point-based discovery (via ``importlib.metadata``).
    """

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        name = plugin.metadata.name
        if name in self._plugins:
            raise PluginError(f"Plugin {name!r} already registered")
        self._plugins[name] = plugin

    def unregister(self, name: str) -> Plugin | None:
        return self._plugins.pop(name, None)

    def get(self, name: str) -> Plugin | None:
        return self._plugins.get(name)

    def list_plugins(self) -> list[PluginMetadata]:
        return [p.metadata for p in self._plugins.values()]

    def setup_all(self, runtime: Any) -> None:
        """Call ``setup(runtime)`` on every registered plugin."""
        for plugin in self._plugins.values():
            plugin.setup(runtime)

    def discover_entry_points(self) -> int:
        """Discover plugins registered via the ``nexus.plugins`` entry-point group.

        Returns the number of plugins discovered and registered.
        """
        try:
            from importlib.metadata import entry_points
        except ImportError:
            return 0

        try:
            eps = entry_points(group="nexus.plugins")
        except TypeError:
            # Python < 3.10 fallback
            all_eps = entry_points()
            fallback: list[Any] = list(all_eps.get("nexus.plugins", []))
            eps = fallback  # type: ignore[assignment]

        count = 0
        for ep in eps:
            try:
                plugin_cls = ep.load()
                plugin = plugin_cls()
                if isinstance(plugin, Plugin) or hasattr(plugin, "metadata"):
                    self.register(plugin)
                    count += 1
            except Exception:
                continue
        return count


_REGISTRY: PluginRegistry | None = None


def get_registry() -> PluginRegistry:
    """Return the process-global plugin registry."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = PluginRegistry()
    return _REGISTRY


__all__ = ["PluginRegistry", "get_registry"]

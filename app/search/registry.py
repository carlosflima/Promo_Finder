"""Registry for enabled search plugins."""
from __future__ import annotations

from .plugin import SearchPlugin


class PluginRegistry:
    def __init__(self):
        self._plugins: dict[str, SearchPlugin] = {}

    def register(self, plugin: SearchPlugin) -> None:
        key = plugin.name.strip().lower()
        if not key:
            raise ValueError("Plugin name cannot be empty")
        self._plugins[key] = plugin

    def remove(self, name: str) -> None:
        self._plugins.pop(name.strip().lower(), None)

    def all(self) -> list[SearchPlugin]:
        return list(self._plugins.values())

    def names(self) -> list[str]:
        return sorted(plugin.name for plugin in self._plugins.values())

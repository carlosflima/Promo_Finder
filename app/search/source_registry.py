"""Registry for concrete, externally supplied price-search connectors."""
from __future__ import annotations

from collections.abc import Callable

from .models import SearchResult

SearchFn = Callable[[str], list[SearchResult]]


class SourceRegistry:
    def __init__(self) -> None:
        self._sources: dict[str, SearchFn] = {}

    def register(self, domain: str, search: SearchFn) -> None:
        normalized = domain.strip().lower().removeprefix("www.")
        if not normalized:
            raise ValueError("domain cannot be empty")
        self._sources[normalized] = search

    def get(self, domain: str) -> SearchFn | None:
        return self._sources.get(domain.strip().lower().removeprefix("www."))

    def domains(self) -> list[str]:
        return sorted(self._sources)

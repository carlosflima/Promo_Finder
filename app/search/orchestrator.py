"""Coordinate enabled search connectors and rank consolidated offers."""
from __future__ import annotations

from collections.abc import Callable

from .models import SearchResult
from .ranking import rank_results
from .source_catalog import SourceCatalog

SearchConnector = Callable[[str], list[SearchResult]]


class SearchOrchestrator:
    def __init__(self, catalog: SourceCatalog, connectors: dict[str, SearchConnector] | None = None):
        self.catalog = catalog
        self.connectors = {key.lower(): value for key, value in (connectors or {}).items()}

    def search(self, query: str, *, ignore_shipping: bool = False) -> list[SearchResult]:
        results: list[SearchResult] = []
        seen: set[tuple[str, str]] = set()
        for source in self.catalog.enabled():
            connector = self.connectors.get(source.domain.lower())
            if connector is None:
                continue
            for result in connector(query):
                key = (result.site.lower(), result.link.lower())
                if key in seen:
                    continue
                seen.add(key)
                results.append(result)
        return rank_results(results, ignore_shipping=ignore_shipping)

"""Coordinate enabled search connectors, shipping quotes and ranking."""
from __future__ import annotations

from collections.abc import Callable

from .models import SearchResult
from .ranking import rank_results
from .source_catalog import SourceCatalog

SearchConnector = Callable[[str], list[SearchResult]]


class SearchOrchestrator:
    def __init__(self, catalog: SourceCatalog, connectors: dict[str, SearchConnector] | None = None, shipping_service=None):
        self.catalog = catalog
        self.connectors = {key.lower(): value for key, value in (connectors or {}).items()}
        self.shipping_service = shipping_service

    def search(self, query: str, *, cep: str | None = None, ignore_shipping: bool = False) -> list[SearchResult]:
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
                if self.shipping_service is not None and cep:
                    quote = self.shipping_service.quote(result, cep, ignore_shipping=ignore_shipping)
                    result = self.shipping_service.apply_quote(result, quote)
                results.append(result)
        return rank_results(results, ignore_shipping=ignore_shipping)

"""Catalog of search sources and their capabilities."""
from dataclasses import dataclass
from enum import StrEnum


class SourceType(StrEnum):
    STORE = "store"
    MARKETPLACE = "marketplace"
    DISCOVERED = "discovered"


@dataclass(frozen=True)
class SearchSource:
    domain: str
    source_type: SourceType
    enabled: bool = True
    supports_shipping: bool = False


class SourceCatalog:
    def __init__(self, sources: list[SearchSource] | None = None):
        self._sources = {source.domain.lower(): source for source in (sources or [])}

    def add(self, source: SearchSource) -> None:
        self._sources[source.domain.lower()] = source

    def enable(self, domain: str) -> None:
        source = self._sources.get(domain.lower())
        if source:
            self._sources[domain.lower()] = SearchSource(
                source.domain, source.source_type, True, source.supports_shipping
            )

    def disable(self, domain: str) -> None:
        source = self._sources.get(domain.lower())
        if source:
            self._sources[domain.lower()] = SearchSource(
                source.domain, source.source_type, False, source.supports_shipping
            )

    def enabled(self) -> list[SearchSource]:
        return [source for source in self._sources.values() if source.enabled]

    def all(self) -> list[SearchSource]:
        return list(self._sources.values())

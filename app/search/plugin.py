"""Plugin contract for store/search adapters."""
from __future__ import annotations

from abc import ABC, abstractmethod
from .models import SearchQuery, SearchResult


class SearchPlugin(ABC):
    name: str = "Unnamed"

    @abstractmethod
    def search(self, query: SearchQuery) -> list[SearchResult]:
        """Return normalized offers for the query."""
        raise NotImplementedError

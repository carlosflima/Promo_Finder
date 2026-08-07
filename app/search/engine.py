"""Parallel, fault-tolerant search orchestration."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable

from app.core.config import settings
from .models import SearchQuery, SearchResult
from .normalizer import search_terms
from .ranking import rank_results, top_per_site

SearchFn = Callable[[str, SearchQuery], Iterable[SearchResult]]


class SearchEngine:
    def __init__(self, searchers: Iterable[SearchFn] = ()):
        self.searchers = list(searchers)

    def search(self, query: SearchQuery, max_per_site: int | None = None) -> list[SearchResult]:
        terms = search_terms(query.term)
        if not terms:
            return []
        results: list[SearchResult] = []
        workers = min(max(1, settings.search_workers), max(1, len(self.searchers)))
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="promo-search") as pool:
            futures = [pool.submit(searcher, term, query) for searcher in self.searchers for term in terms]
            for future in as_completed(futures):
                try:
                    results.extend(future.result())
                except Exception:
                    # One blocked store must not cancel the whole search.
                    continue
        deduped = self._deduplicate(results)
        return top_per_site(rank_results(deduped, query.ignore_shipping), max_per_site or settings.max_items_per_site)

    @staticmethod
    def _deduplicate(results: list[SearchResult]) -> list[SearchResult]:
        seen: set[tuple[str, str, float]] = set()
        output: list[SearchResult] = []
        for result in results:
            key = (result.site.lower().strip(), result.link.strip(), round(result.price, 2))
            if not result.link or key in seen:
                continue
            seen.add(key)
            output.append(result)
        return output

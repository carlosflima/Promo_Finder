"""Parallel, fault-tolerant search orchestration."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from typing import Callable, Iterable

from app.core.config import settings
from .models import SearchQuery, SearchResult
from .normalizer import search_terms
from .plugin import SearchPlugin
from .ranking import rank_results
from .selection import select_sites

SearchFn = Callable[[str, SearchQuery], Iterable[SearchResult]]
SearchSource = SearchFn | SearchPlugin


class SearchEngine:
    def __init__(self, searchers: Iterable[SearchSource] = ()):
        self.searchers = list(searchers)

    def search(self, query: SearchQuery, max_per_site: int | None = None) -> list[SearchResult]:
        terms = search_terms(query.term)
        if not terms or not self.searchers:
            return []

        results: list[SearchResult] = []
        workers = min(max(1, settings.search_workers), max(1, len(self.searchers) * len(terms)))
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="promo-search") as pool:
            futures = [
                pool.submit(self._run_source, source, term, query)
                for source in self.searchers
                for term in terms
            ]
            for future in as_completed(futures):
                try:
                    results.extend(future.result())
                except Exception:
                    # One blocked store must not cancel the whole search.
                    continue

        deduped = self._deduplicate(results)
        ranked = rank_results(deduped, query.ignore_shipping)
        return select_sites(
            ranked,
            required_sites=query.required_sites,
            top_site_count=query.top_site_count,
            max_per_site=max_per_site or query.max_items_per_site or settings.max_items_per_site,
        )

    @staticmethod
    def _run_source(source: SearchSource, term: str, query: SearchQuery) -> Iterable[SearchResult]:
        term_query = replace(query, term=term)
        if isinstance(source, SearchPlugin):
            return source.search(term_query)
        return source(term, term_query)

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

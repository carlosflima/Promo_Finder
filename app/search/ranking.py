"""Deterministic offer ranking."""
from __future__ import annotations

from .models import SearchResult


def rank_results(results: list[SearchResult], ignore_shipping: bool = False) -> list[SearchResult]:
    def key(item: SearchResult):
        shipping = 0 if ignore_shipping else (item.shipping if item.shipping is not None else 0)
        # Lower total cost wins. Tie-break with promotional status and seller/site.
        return (item.price + shipping, not item.promotional, -item.source_priority, item.site.lower(), item.title.lower())

    return sorted(results, key=key)


def top_per_site(results: list[SearchResult], limit: int = 5) -> list[SearchResult]:
    grouped: dict[str, list[SearchResult]] = {}
    for result in results:
        grouped.setdefault(result.site, []).append(result)
    selected: list[SearchResult] = []
    for site, items in grouped.items():
        selected.extend(rank_results(items)[:limit])
    return rank_results(selected)

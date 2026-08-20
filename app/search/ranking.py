"""Deterministic offer ranking."""
from __future__ import annotations

from .models import SearchResult


def rank_results(results: list[SearchResult], ignore_shipping: bool = False):
    def key(item: SearchResult):
        # A missing shipping quote must not masquerade as free shipping.
        shipping_known = ignore_shipping or item.shipping is not None
        shipping = 0.0 if ignore_shipping else (item.shipping if shipping_known else 0.0)
        return (
            not shipping_known,
            item.price + shipping,
            not item.promotional,
            -item.source_priority,
            item.site.lower(),
            item.title.lower(),
        )

    return sorted(results, key=key)


def top_per_site(results: list[SearchResult], limit: int = 5):
    grouped: dict[str, list[SearchResult]] = {}
    for result in results:
        grouped.setdefault(result.site, []).append(result)
    selected: list[SearchResult] = []
    for site, items in grouped.items():
        selected.extend(rank_results(items)[:limit])
    return rank_results(selected)

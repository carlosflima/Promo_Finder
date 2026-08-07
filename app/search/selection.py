"""Offer/site selection rules for the comparison result."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .models import SearchResult


def select_sites(
    results: Iterable[SearchResult],
    required_sites: Iterable[str] = (),
    top_site_count: int = 3,
    max_per_site: int = 5,
) -> list[SearchResult]:
    """Return the N cheapest sites plus all explicitly requested sites.

    Top-N is based on the cheapest offer found per site, not on a predefined
    ranking of stores. Explicit sites are retained even when outside Top-N.
    """
    grouped: dict[str, list[SearchResult]] = defaultdict(list)
    for result in results:
        grouped[result.site.strip().lower()].append(result)

    required = {site.strip().lower() for site in required_sites if site.strip()}
    ranked_sites = sorted(
        grouped,
        key=lambda key: min((item.total_price for item in grouped[key]), default=float("inf")),
    )
    selected = set(ranked_sites[: max(0, top_site_count)]) | required

    output: list[SearchResult] = []
    for key in selected:
        offers = sorted(
            grouped.get(key, []),
            key=lambda item: (item.total_price, item.price, item.title.lower()),
        )
        output.extend(offers[: max(0, max_per_site)])

    return sorted(
        output,
        key=lambda item: (item.total_price, item.price, item.site.lower(), item.title.lower()),
    )

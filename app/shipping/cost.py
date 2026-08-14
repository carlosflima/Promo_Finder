"""Helpers for ranking offers by verified effective cost."""
from app.search.models import SearchResult


def effective_cost(result: SearchResult) -> float:
    """Return product price plus the currently applied shipping amount."""
    return float(result.price) + float(result.shipping)


def rank_by_effective_cost(results: list[SearchResult]) -> list[SearchResult]:
    """Sort only by values actually present on the offer."""
    return sorted(results, key=effective_cost)

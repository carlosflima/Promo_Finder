"""Small provider registry used by the shipping orchestration layer.

Real store adapters can be registered here without coupling search/ranking to a
specific HTTP client. Providers must return a verified ShippingQuote.
"""
from collections.abc import Callable

from app.search.models import SearchResult

from .models import ShippingQuote

ShippingProvider = Callable[[str, SearchResult], ShippingQuote]


def register_provider(
    registry: dict[str, ShippingProvider], site: str, provider: ShippingProvider
) -> dict[str, ShippingProvider]:
    key = site.strip().lower()
    if not key:
        raise ValueError("site cannot be empty")
    registry[key] = provider
    return registry

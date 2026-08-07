"""Shipping service boundary.

The service keeps the search/ranking layers independent from CEP/shipping
providers. Real store or marketplace adapters can be registered later.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from app.search.models import SearchResult

from .cep import normalize_cep
from .models import ShippingQuote

ShippingProvider = Callable[[str, SearchResult], ShippingQuote]


class ShippingService:
    def __init__(self, providers: dict[str, ShippingProvider] | None = None):
        self.providers = {key.lower(): value for key, value in (providers or {}).items()}

    def quote(self, result: SearchResult, cep: str, ignore_shipping: bool = False) -> ShippingQuote:
        normalized_cep = normalize_cep(cep)
        if ignore_shipping:
            return ShippingQuote(
                cep=normalized_cep,
                amount=0.0,
                free_shipping=True,
                provider="ignored",
                message="Frete ignorado pelo usuário.",
            )

        provider = self.providers.get(result.site.lower())
        if provider is None:
            return ShippingQuote(
                cep=normalized_cep,
                amount=result.shipping,
                free_shipping=result.shipping == 0,
                provider="offer",
                message="Frete ainda não consultado no provedor da loja.",
            )
        return provider(normalized_cep, result)

    def apply_quote(self, result: SearchResult, quote: ShippingQuote) -> SearchResult:
        return replace(
            result,
            shipping=quote.effective_amount,
            metadata={**result.metadata, "shipping_provider": quote.provider, "shipping_available": quote.available},
        )

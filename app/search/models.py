"""Canonical search query and offer models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class SearchQuery:
    term: str
    cep: Optional[str] = None
    ignore_shipping: bool = False
    required_sites: tuple[str, ...] = ()
    discover_sites: bool = True
    top_site_count: int = 3
    max_items_per_site: int = 5


@dataclass
class SearchResult:
    title: str
    price: float
    site: str
    link: str
    seller: str = ""
    shipping: Optional[float] = None
    free_shipping_from: Optional[float] = None
    promotional: bool = False
    promotion: str = ""
    rating: Optional[float] = None
    seller_rating: Optional[float] = None
    source_priority: int = 0
    metadata: dict = field(default_factory=dict)

    @property
    def total_price(self) -> float:
        if self.shipping is None:
            return self.price
        return self.price + self.shipping

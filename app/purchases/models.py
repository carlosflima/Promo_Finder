"""Canonical purchase-list models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from app.search.models import SearchResult


@dataclass
class PurchaseItem:
    product: str
    quantity: int
    offer: SearchResult
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise ValueError("quantity must be greater than zero")

    @property
    def total(self) -> float:
        return self.offer.total_price * self.quantity


@dataclass
class PurchaseList:
    name: str
    items: list[PurchaseItem] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))

    def add(self, item: PurchaseItem) -> None:
        self.items.append(item)

    def remove(self, item_id: str) -> bool:
        before = len(self.items)
        self.items = [item for item in self.items if item.id != item_id]
        return len(self.items) != before

    @property
    def total(self) -> float:
        return sum(item.total for item in self.items)

    def seller_groups(self) -> dict[tuple[str, str], list[PurchaseItem]]:
        """Group offers by site/seller for safe marketplace checkout."""
        groups: dict[tuple[str, str], list[PurchaseItem]] = {}
        for item in self.items:
            seller = item.offer.seller or "__direct_store__"
            key = (item.offer.site.lower(), seller.lower())
            groups.setdefault(key, []).append(item)
        return groups

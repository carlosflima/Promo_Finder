"""Selection helpers for generated store/seller shopping lists."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .marketplace import MarketplaceService, SellerIdentity
from .models import SearchResult


@dataclass(frozen=True)
class PurchaseGroup:
    """A set of offers that can be sent to the same purchase destination."""

    site: str
    seller: str
    seller_id: str
    marketplace: bool
    offers: tuple[SearchResult, ...]

    @property
    def identity(self) -> SellerIdentity:
        return SellerIdentity(self.site, self.seller, self.seller_id)

    @property
    def total(self) -> float:
        return sum(item.total_price for item in self.offers)


class PurchaseListSelector:
    def __init__(self, marketplace: MarketplaceService | None = None) -> None:
        self.marketplace = marketplace or MarketplaceService()

    def groups(self, offers: Iterable[SearchResult]) -> list[PurchaseGroup]:
        """Create valid purchase groups without mixing marketplace sellers."""
        grouped: dict[str, list[SearchResult]] = {}
        representatives: dict[str, SearchResult] = {}
        for offer in offers:
            identity = self.marketplace.identity(offer)
            grouped.setdefault(identity.key, []).append(offer)
            representatives.setdefault(identity.key, offer)

        result: list[PurchaseGroup] = []
        for key, items in grouped.items():
            representative = representatives[key]
            identity = self.marketplace.identity(representative)
            result.append(
                PurchaseGroup(
                    site=identity.site,
                    seller=identity.seller,
                    seller_id=identity.seller_id,
                    marketplace=representative.marketplace,
                    offers=tuple(items),
                )
            )
        return sorted(result, key=lambda group: group.total)

    def select_group(
        self,
        offers: Iterable[SearchResult],
        site: str,
        seller: str = "",
        seller_id: str = "",
    ) -> list[SearchResult]:
        """Return only offers belonging to the requested purchase destination."""
        return self.marketplace.filter_for_seller(offers, site, seller, seller_id)

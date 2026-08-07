"""Marketplace and seller rules for offers and shopping lists.

This module deliberately keeps marketplace policy independent from scraping.
A plugin only needs to provide the marketplace/seller metadata; this layer
applies the business rules consistently across all connectors.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import SearchResult


@dataclass(frozen=True)
class SellerIdentity:
    """Stable identity used to group offers from the same marketplace seller."""

    site: str
    seller: str
    seller_id: str = ""

    @property
    def key(self) -> str:
        seller_key = self.seller_id.strip() or self.seller.strip().casefold()
        return f"{self.site.strip().casefold()}::{seller_key}"


class MarketplaceService:
    """Classify offers and enforce seller-safe list selection."""

    def identity(self, offer: SearchResult) -> SellerIdentity:
        seller_id = str(offer.metadata.get("seller_id", "")).strip()
        seller = offer.seller.strip()
        if not seller and not offer.marketplace:
            seller = offer.site
        return SellerIdentity(site=offer.site, seller=seller, seller_id=seller_id)

    def group_by_seller(
        self, offers: Iterable[SearchResult]
    ) -> dict[str, list[SearchResult]]:
        groups: dict[str, list[SearchResult]] = {}
        for offer in offers:
            key = self.identity(offer).key
            groups.setdefault(key, []).append(offer)
        return groups

    def can_share_purchase_list(
        self, offers: Iterable[SearchResult], ignore_shipping: bool = False
    ) -> bool:
        """Return whether offers can safely belong to one generated list.

        Direct stores can share a list. Marketplace offers must belong to the
        same marketplace seller. ``ignore_shipping`` only controls whether
        shipping is considered in the list cost; it never disables seller
        isolation.
        """
        selected = list(offers)
        if not selected:
            return False

        marketplaces = [offer for offer in selected if offer.marketplace]
        if not marketplaces:
            return True

        identities = {self.identity(offer).key for offer in marketplaces}
        return len(identities) == 1

    def filter_for_seller(
        self,
        offers: Iterable[SearchResult],
        site: str,
        seller: str,
        seller_id: str = "",
    ) -> list[SearchResult]:
        target = SellerIdentity(site, seller, seller_id).key
        return [offer for offer in offers if self.identity(offer).key == target]

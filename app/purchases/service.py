"""Application service for safe purchase-list construction."""
from __future__ import annotations

from collections import defaultdict

from app.search.models import SearchResult
from .models import PurchaseItem, PurchaseList


class PurchaseListService:
    def create(self, name: str) -> PurchaseList:
        if not name.strip():
            raise ValueError("purchase list name is required")
        return PurchaseList(name=name.strip())

    def add_offer(
        self,
        purchase_list: PurchaseList,
        product: str,
        offer: SearchResult,
        quantity: int = 1,
    ) -> PurchaseItem:
        item = PurchaseItem(product=product.strip(), quantity=quantity, offer=offer)
        if not item.product:
            raise ValueError("product name is required")
        self._validate_marketplace_isolation(purchase_list, offer)
        purchase_list.add(item)
        return item

    def remove_offer(self, purchase_list: PurchaseList, item_id: str) -> bool:
        return purchase_list.remove(item_id)

    def by_checkout_target(self, purchase_list: PurchaseList) -> dict[tuple[str, str], list[PurchaseItem]]:
        return purchase_list.seller_groups()

    @staticmethod
    def _validate_marketplace_isolation(
        purchase_list: PurchaseList, offer: SearchResult
    ) -> None:
        if not offer.marketplace:
            return
        seller = (offer.seller or "").strip().lower()
        site = offer.site.strip().lower()
        if not seller:
            raise ValueError("marketplace offer requires seller identity")
        for item in purchase_list.items:
            current = item.offer
            if current.marketplace and current.site.strip().lower() == site:
                current_seller = (current.seller or "").strip().lower()
                if current_seller != seller:
                    raise ValueError(
                        "marketplace purchase lists cannot mix different sellers"
                    )

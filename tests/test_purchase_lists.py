import pytest

from app.purchases import PurchaseListService
from app.search.models import SearchResult


def offer(site="Loja", seller="", marketplace=False, price=10.0):
    return SearchResult(
        title="Produto",
        price=price,
        site=site,
        link="https://example.com/produto",
        seller=seller,
        marketplace=marketplace,
    )


def test_purchase_list_totals_quantity_and_shipping():
    service = PurchaseListService()
    purchase_list = service.create("Mercado")
    service.add_offer(purchase_list, "Arroz", offer(price=20, site="Loja A"), 2)
    assert purchase_list.total == 40


def test_marketplace_same_seller_can_be_grouped():
    service = PurchaseListService()
    purchase_list = service.create("Marketplace")
    service.add_offer(purchase_list, "A", offer(site="Market", seller="seller-1", marketplace=True))
    service.add_offer(purchase_list, "B", offer(site="Market", seller="seller-1", marketplace=True))
    assert len(purchase_list.seller_groups()) == 1


def test_marketplace_different_sellers_are_rejected():
    service = PurchaseListService()
    purchase_list = service.create("Marketplace")
    service.add_offer(purchase_list, "A", offer(site="Market", seller="seller-1", marketplace=True))
    with pytest.raises(ValueError, match="cannot mix different sellers"):
        service.add_offer(
            purchase_list,
            "B",
            offer(site="Market", seller="seller-2", marketplace=True),
        )


def test_direct_store_offers_do_not_require_seller():
    service = PurchaseListService()
    purchase_list = service.create("Loja")
    service.add_offer(purchase_list, "A", offer(site="Loja A"))
    service.add_offer(purchase_list, "B", offer(site="Loja A"))
    assert len(purchase_list.seller_groups()) == 1

from app.search.marketplace import MarketplaceService
from app.search.list_selection import PurchaseListSelector
from app.search.models import SearchResult


def offer(title, site, seller, marketplace=True, seller_id=""):
    return SearchResult(
        title=title,
        price=100.0,
        site=site,
        link=f"https://example.com/{title}",
        seller=seller,
        marketplace=marketplace,
        metadata={"seller_id": seller_id} if seller_id else {},
    )


def test_marketplace_offers_from_different_sellers_cannot_share_list():
    service = MarketplaceService()
    a = offer("A", "Marketplace", "Seller A", seller_id="a")
    b = offer("B", "Marketplace", "Seller B", seller_id="b")
    assert not service.can_share_purchase_list([a, b])


def test_same_marketplace_seller_can_share_list():
    service = MarketplaceService()
    a = offer("A", "Marketplace", "Seller A", seller_id="a")
    b = offer("B", "Marketplace", "Seller A", seller_id="a")
    assert service.can_share_purchase_list([a, b])


def test_direct_store_offers_can_share_list():
    service = MarketplaceService()
    a = offer("A", "Store", "", marketplace=False)
    b = offer("B", "Store", "", marketplace=False)
    assert service.can_share_purchase_list([a, b])


def test_purchase_groups_keep_sellers_separate():
    selector = PurchaseListSelector()
    offers = [
        offer("A", "Marketplace", "Seller A", seller_id="a"),
        offer("B", "Marketplace", "Seller B", seller_id="b"),
        offer("C", "Marketplace", "Seller A", seller_id="a"),
    ]
    groups = selector.groups(offers)
    assert len(groups) == 2
    assert sorted(len(group.offers) for group in groups) == [1, 2]

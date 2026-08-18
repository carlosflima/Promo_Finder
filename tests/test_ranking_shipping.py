from app.search.models import SearchResult
from app.search.ranking import rank_results


def offer(site, price, shipping):
    return SearchResult(title=site, price=price, site=site, link=f"https://{site}/p", shipping=shipping)


def test_known_shipping_is_ranked_before_unknown_shipping():
    results = [offer("unknown", 80, None), offer("quoted", 90, 5)]
    ranked = rank_results(results)
    assert ranked[0].site == "quoted"


def test_ignore_shipping_uses_product_price_only():
    results = [offer("a", 100, 1), offer("b", 90, 50)]
    ranked = rank_results(results, ignore_shipping=True)
    assert [item.site for item in ranked] == ["b", "a"]

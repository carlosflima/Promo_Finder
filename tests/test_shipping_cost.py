from app.search.models import SearchResult
from app.shipping.cost import effective_cost, rank_by_effective_cost


def offer(price, shipping):
    return SearchResult(site="shop", title="item", price=price, shipping=shipping, url="https://shop/item")


def test_effective_cost_includes_shipping():
    assert effective_cost(offer(100, 15)) == 115


def test_rank_uses_effective_cost():
    results = [offer(100, 30), offer(105, 5), offer(90, 20)]
    assert [effective_cost(r) for r in rank_by_effective_cost(results)] == [110, 110, 130]

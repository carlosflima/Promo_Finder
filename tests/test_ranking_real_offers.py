from app.search.models import SearchResult
from app.search.ranking import rank_results


def offer(price, shipping, promotional=False, site="shop.example"):
    return SearchResult(title="produto", price=price, site=site, link=f"https://{site}/{price}", shipping=shipping, promotional=promotional)


def test_known_total_cost_beats_unknown_shipping():
    results = [offer(80, None), offer(90, 5)]
    ranked = rank_results(results)
    assert ranked[0].total_price == 95
    assert ranked[1].shipping is None


def test_promotional_offer_breaks_equal_cost_tie():
    results = [offer(100, 0), offer(100, 0, promotional=True)]
    ranked = rank_results(results)
    assert ranked[0].promotional is True

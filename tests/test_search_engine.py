from app.search.engine import SearchEngine
from app.search.models import SearchQuery, SearchResult


def make_searcher(site, price):
    def search(term, query):
        return [SearchResult(title=f"{term} produto", price=price, site=site, link=f"https://{site}.com/p/{term}")]
    return search


def test_search_engine_ranks_lowest_price_first():
    engine = SearchEngine([make_searcher("loja-a", 100), make_searcher("loja-b", 80)])
    results = engine.search(SearchQuery("Cafe"))
    assert [item.price for item in results] == [80, 100]


def test_search_engine_ignores_failed_searcher():
    def failing(term, query):
        raise RuntimeError("site unavailable")

    engine = SearchEngine([failing, make_searcher("loja", 50)])
    results = engine.search(SearchQuery("Cafe"))
    assert len(results) == 1
    assert results[0].price == 50

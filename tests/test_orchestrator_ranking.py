from app.search.models import SearchResult
from app.search.orchestrator import SearchOrchestrator
from app.search.source_catalog import SearchSource, SourceCatalog, SourceType


def test_orchestrator_returns_real_sources_ranked_by_known_total_cost():
    catalog = SourceCatalog([
        SearchSource("a.example", SourceType.STORE),
        SearchSource("b.example", SourceType.STORE),
    ])

    def a(_):
        return [SearchResult(site="a.example", title="item", price=100, shipping=20, link="https://a/item")]

    def b(_):
        return [SearchResult(site="b.example", title="item", price=110, shipping=0, link="https://b/item", promotional=True)]

    results = SearchOrchestrator(catalog, {"a.example": a, "b.example": b}).search("item")
    assert [r.site for r in results] == ["b.example", "a.example"]

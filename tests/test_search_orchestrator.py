from app.search.models import SearchResult
from app.search.orchestrator import SearchOrchestrator
from app.search.source_catalog import SearchSource, SourceCatalog, SourceType


def result(site, link):
    return SearchResult(site=site, title="produto", price=10, link=link)


def test_orchestrator_calls_only_enabled_connectors_and_deduplicates():
    catalog = SourceCatalog([
        SearchSource("a.example", SourceType.STORE),
        SearchSource("b.example", SourceType.STORE, enabled=False),
    ])
    calls = []

    def connector(query):
        calls.append(query)
        return [result("a.example", "https://a.example/p"), result("a.example", "https://a.example/p")]

    orchestrator = SearchOrchestrator(catalog, {"a.example": connector})
    results = orchestrator.search("notebook")
    assert calls == ["notebook"]
    assert len(results) == 1
    assert results[0].link.endswith("/p")

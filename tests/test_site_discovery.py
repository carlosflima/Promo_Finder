from app.search.models import SearchResult
from app.search.site_discovery import discover_candidate_sites


def result(site, price, link=None):
    return SearchResult(
        site=site,
        title="produto",
        price=price,
        link=link or f"https://{site}/produto",
    )


def test_discovery_uses_lowest_effective_cost_and_keeps_explicit_sites():
    results = [
        result("cheap.example", 10),
        result("mid.example", 20),
        result("expensive.example", 30),
    ]
    assert discover_candidate_sites(results, ["https://required.example"], 2) == [
        "required.example", "cheap.example", "mid.example"
    ]


def test_discovery_normalizes_www_and_does_not_duplicate_explicit_site():
    results = [result("www.cheap.example", 10)]
    assert discover_candidate_sites(results, ["cheap.example"], 3) == ["cheap.example"]

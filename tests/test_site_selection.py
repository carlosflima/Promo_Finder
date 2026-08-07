from app.search.models import SearchResult
from app.search.selection import select_sites
from app.search.site import site_name, validate_site_url


def offer(site: str, price: float, title: str = "Produto") -> SearchResult:
    return SearchResult(title=title, price=price, site=site, link=f"https://{site}/p/{price}")


def test_top_three_are_the_three_cheapest_sites():
    results = [
        offer("a.com.br", 100),
        offer("b.com.br", 80),
        offer("c.com.br", 120),
        offer("d.com.br", 90),
    ]
    selected = select_sites(results, top_site_count=3, max_per_site=5)
    assert {item.site for item in selected} == {"a.com.br", "b.com.br", "d.com.br"}


def test_required_site_is_kept_even_when_not_top_three():
    results = [offer("a.com.br", 10), offer("b.com.br", 20), offer("c.com.br", 30), offer("d.com.br", 100)]
    selected = select_sites(results, required_sites=["d.com.br"], top_site_count=3)
    assert "d.com.br" in {item.site for item in selected}


def test_only_five_offers_per_site_are_returned():
    results = [offer("a.com.br", price) for price in range(1, 9)]
    selected = select_sites(results, top_site_count=3, max_per_site=5)
    assert len(selected) == 5
    assert [item.price for item in selected] == [1, 2, 3, 4, 5]


def test_url_is_normalized_and_local_hosts_are_rejected():
    assert validate_site_url("site.com.br") == "https://site.com.br"
    assert site_name("https://www.site.com.br") == "site.com.br"
    try:
        validate_site_url("http://127.0.0.1:8000")
        assert False, "local host should be rejected"
    except ValueError:
        pass

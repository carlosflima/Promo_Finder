from app.search.first_real_source import RealPriceSource
from app.search.http_connector import HttpConnector, HttpPolicy


def test_real_source_uses_injected_endpoint_and_normalizer():
    calls = []

    def request(url, **kwargs):
        calls.append((url, kwargs))
        return {"items": [{"name": "Notebook", "price": 1999.9, "url": "https://shop.example/notebook"}]}

    source = RealPriceSource(
        "shop.example",
        HttpConnector(request, HttpPolicy(retries=0)),
        "https://api.example/search",
        lambda payload: payload["items"],
    )
    results = source.search("notebook")
    assert calls[0][1]["params"] == {"q": "notebook"}
    assert results[0].title == "Notebook"
    assert results[0].price == 1999.9

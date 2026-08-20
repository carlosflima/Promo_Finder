import pytest

from app.search.mercadolivre import MercadoLivreConnector
from app.search.http_connector import HttpConnector, HttpPolicy


def test_mercadolivre_normalizes_promotional_result():
    def request(url, **kwargs):
        return {
            "results": [{
                "title": "Console",
                "price": 1999.0,
                "original_price": 2299.0,
                "permalink": "https://mercadolivre.com.br/item/1",
                "seller": {"nickname": "loja"},
                "shipping": {"cost": 0},
            }]
        }

    connector = MercadoLivreConnector(HttpConnector(request, HttpPolicy(retries=0)), "https://api.example/items", "token")
    result = connector.search("console")[0]
    assert result.price == 1999.0
    assert result.promotional is True
    assert result.promotion == "Preço promocional"
    assert result.marketplace is True
    assert result.seller == "loja"


def test_mercadolivre_requires_token():
    with pytest.raises(ValueError):
        MercadoLivreConnector(HttpConnector(lambda *a, **k: {}, HttpPolicy()), "https://api.example/items", "")

from app.search.result_normalizer import normalize_result


def test_promotional_price_is_used_and_regular_price_preserved():
    result = normalize_result({
        "site": "shop.example",
        "name": "Notebook",
        "price": 3000,
        "promotional_price": 2499.90,
        "regular_price": 3000,
        "promotion": "Oferta relâmpago",
        "url": "https://shop.example/notebook",
    }, source="fallback.example")
    assert result.price == 2499.90
    assert result.promotional is True
    assert result.promotion == "Oferta relâmpago"
    assert result.metadata["regular_price"] == 3000


def test_shipping_and_marketplace_fields_are_normalized():
    result = normalize_result({
        "name": "Produto",
        "price": 100,
        "shipping": 15.5,
        "seller": "Loja A",
        "rating": 4.7,
        "seller_rating": 4.9,
        "marketplace": True,
    }, source="market.example")
    assert result.site == "market.example"
    assert result.total_price == 115.5
    assert result.marketplace is True
    assert result.seller == "Loja A"

from app.search.offer_normalizer import normalize_offer


def test_promotional_price_becomes_search_price():
    result = normalize_offer(
        {
            "site": "Shop",
            "name": "Notebook",
            "price": 3999,
            "regular_price": 4499,
            "promotional_price": 3799,
            "promotion_description": "Oferta relâmpago",
            "url": "https://shop.example/notebook",
        },
        source="shop.example",
    )
    assert result.price == 3799
    assert result.promotional is True
    assert result.promotion == "Oferta relâmpago"
    assert result.metadata["regular_price"] == 4499


def test_missing_optional_fields_are_safe():
    result = normalize_offer({"title": "Produto", "price": 10}, source="example.com")
    assert result.site == "example.com"
    assert result.link == ""
    assert result.shipping is None

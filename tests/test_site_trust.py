from app.search.site_trust import assess_site


def test_https_site_with_product_url_is_trusted():
    trust = assess_site("https://shop.example/item/1")
    assert trust.https is True
    assert trust.has_product_url is True
    assert trust.score == 100
    assert trust.trusted is True


def test_http_site_is_not_marked_trusted():
    trust = assess_site("http://shop.example/item/1")
    assert trust.https is False
    assert trust.score == 40
    assert trust.trusted is False


def test_domain_is_normalized():
    trust = assess_site("https://WWW.Example.com/item")
    assert trust.domain == "example.com"

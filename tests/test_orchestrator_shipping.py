from app.search.models import SearchResult
from app.search.orchestrator import SearchOrchestrator
from app.search.source_catalog import SearchSource, SourceCatalog, SourceType
from app.shipping.models import ShippingQuote


class FakeShipping:
    def quote(self, result, cep, ignore_shipping=False):
        assert cep == "13050000"
        return ShippingQuote(cep=cep, amount=7.5, free_shipping=False, provider="test", available=True)

    def apply_quote(self, result, quote):
        result.shipping = quote.amount
        return result


def test_orchestrator_applies_shipping_before_ranking():
    catalog = SourceCatalog([SearchSource("shop.example", SourceType.STORE)])
    connector = lambda _: [SearchResult(site="shop.example", title="item", price=100, shipping=0, link="https://shop/item")]
    results = SearchOrchestrator(catalog, {"shop.example": connector}, FakeShipping()).search("item", cep="13050000")
    assert results[0].shipping == 7.5

from app.search.models import SearchResult
from app.shipping.cep import format_cep, normalize_cep
from app.shipping.models import ShippingQuote
from app.shipping.service import ShippingService


def result():
    return SearchResult(title="Produto", price=100.0, site="loja.com.br", link="https://loja.com.br/p/1")


def test_cep_is_normalized_and_formatted():
    assert normalize_cep("01001-000") == "01001000"
    assert format_cep("01001000") == "01001-000"


def test_invalid_cep_is_rejected():
    for value in ("", "123", "123456789", "abcde-fgh"):
        try:
            normalize_cep(value)
            assert False, "invalid CEP should raise"
        except ValueError:
            pass


def test_ignore_shipping_returns_zero_cost_quote():
    quote = ShippingService().quote(result(), "01001-000", ignore_shipping=True)
    assert quote.free_shipping is True
    assert quote.effective_amount == 0.0
    assert quote.provider == "ignored"


def test_provider_quote_can_be_applied_to_offer():
    service = ShippingService({"loja.com.br": lambda cep, item: ShippingQuote(cep, 12.5, provider="test")})
    quoted = service.quote(result(), "01001-000")
    updated = service.apply_quote(result(), quoted)
    assert quoted.amount == 12.5
    assert updated.shipping == 12.5
    assert updated.total_price == 112.5

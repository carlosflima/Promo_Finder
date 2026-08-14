import pytest

from app.shipping.providers import register_provider


def test_register_provider_normalizes_site():
    registry = {}
    provider = object()
    register_provider(registry, " Example.COM ", provider)
    assert registry["example.com"] is provider


def test_register_provider_rejects_empty_site():
    with pytest.raises(ValueError):
        register_provider({}, "   ", object())

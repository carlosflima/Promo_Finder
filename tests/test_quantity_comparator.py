from decimal import Decimal

import pytest

from app.services.quantity_comparator import compare_offers


def test_lower_price_per_quantity_wins():
    result = compare_offers([
        {"id": "a", "title": "Pacote menor", "price": 20, "comparable_quantity": 1},
        {"id": "b", "title": "Pacote maior", "price": 30, "comparable_quantity": 2},
    ])
    assert result[0].offer_id == "b"
    assert result[0].is_best_value is True
    assert result[0].price_per_quantity == Decimal("15.0000")


def test_invalid_or_zero_quantity_is_ignored():
    result = compare_offers([
        {"id": "bad", "title": "Inválido", "price": 10, "comparable_quantity": 0},
        {"id": "ok", "title": "Válido", "price": 12, "comparable_quantity": 1},
    ])
    assert [item.offer_id for item in result] == ["ok"]


def test_empty_result():
    assert compare_offers([]) == []


def test_invalid_price_raises():
    with pytest.raises(ValueError):
        compare_offers([{"id": "x", "title": "X", "price": "abc", "comparable_quantity": 1}])

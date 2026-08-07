from datetime import datetime, timedelta

import pytest

from app.history.models import HistoryFilter, PriceObservation
from app.history.service import PriceHistoryService


def observation(day, price, promo=False):
    return PriceObservation(
        search_id="s1", product_key="coffee", product_name="Coffee", site="Loja A",
        price=price, promotional=promo, observed_at=datetime(2026, 8, 1) + timedelta(days=day)
    )


def test_empty_filter_returns_no_history():
    service = PriceHistoryService([observation(0, 20)])
    assert service.search() == []


def test_date_and_product_filter():
    service = PriceHistoryService([observation(0, 20), observation(2, 18)])
    result = service.search(HistoryFilter(date_from=datetime(2026, 8, 2), product_key="coffee"))
    assert len(result) == 1
    assert result[0].price == 18


def test_baseline_and_real_promotion_score():
    service = PriceHistoryService([observation(0, 20), observation(1, 22), observation(2, 18)])
    current = observation(3, 15, promo=True)
    assert service.baseline("coffee", "Loja A") == 20
    assert service.promotion_score(current) == 25


def test_negative_values_are_rejected():
    service = PriceHistoryService()
    with pytest.raises(ValueError):
        service.record(observation(0, -1))

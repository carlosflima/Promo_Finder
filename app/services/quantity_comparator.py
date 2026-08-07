"""Compare equivalent offers without exposing package-size fields in the UI.

The comparator consumes normalized offers. A caller may provide a comparable
quantity for each offer (for example, number of items represented by the
package) while the public product form remains quantity-free.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable


@dataclass(frozen=True)
class QuantityComparison:
    offer_id: str
    title: str
    price: Decimal
    comparable_quantity: Decimal
    price_per_quantity: Decimal
    is_best_value: bool = False
    savings_percent: Decimal = Decimal("0")


def _decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"Valor numérico inválido: {value!r}") from exc


def compare_offers(offers: Iterable[dict[str, Any]]) -> list[QuantityComparison]:
    """Return offers ordered by normalized price and mark the best value.

    ``comparable_quantity`` is deliberately optional at the transport layer,
    but offers without a positive quantity cannot participate in the
    comparison. This prevents division-by-zero and misleading suggestions.
    """
    comparisons: list[QuantityComparison] = []
    for offer in offers:
        price = _decimal(offer.get("price"))
        quantity = _decimal(offer.get("comparable_quantity", 1))
        if price < 0 or quantity <= 0:
            continue
        comparisons.append(
            QuantityComparison(
                offer_id=str(offer.get("id", "")),
                title=str(offer.get("title", "")),
                price=price,
                comparable_quantity=quantity,
                price_per_quantity=(price / quantity).quantize(Decimal("0.0001")),
            )
        )

    comparisons.sort(key=lambda item: (item.price_per_quantity, item.price, item.title.lower()))
    if not comparisons:
        return []

    best = comparisons[0].price_per_quantity
    result: list[QuantityComparison] = []
    for index, item in enumerate(comparisons):
        savings = Decimal("0") if best == 0 else ((item.price_per_quantity - best) / item.price_per_quantity * 100).quantize(Decimal("0.01"))
        result.append(
            QuantityComparison(
                offer_id=item.offer_id,
                title=item.title,
                price=item.price,
                comparable_quantity=item.comparable_quantity,
                price_per_quantity=item.price_per_quantity,
                is_best_value=index == 0,
                savings_percent=savings,
            )
        )
    return result

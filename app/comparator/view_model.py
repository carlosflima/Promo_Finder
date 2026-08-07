from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class ComparatorColumn:
    """A stable column in the horizontal comparison table."""

    site: str
    seller: str | None
    offers: tuple[dict[str, Any], ...]


def build_columns(offers: Iterable[dict[str, Any]]) -> list[ComparatorColumn]:
    """Group offers by site/seller and keep each column ordered by total cost."""
    groups: dict[tuple[str, str | None], list[dict[str, Any]]] = {}
    for offer in offers:
        site = str(offer.get("site") or "").strip()
        seller = offer.get("seller")
        key = (site, str(seller).strip() if seller else None)
        groups.setdefault(key, []).append(dict(offer))

    columns = []
    for (site, seller), values in groups.items():
        values.sort(key=lambda item: float(item.get("total_price") or item.get("price") or 0))
        columns.append(ComparatorColumn(site=site, seller=seller, offers=tuple(values[:5])))

    columns.sort(key=lambda column: min(
        float(item.get("total_price") or item.get("price") or 0)
        for item in column.offers
    ) if column.offers else float("inf"))
    return columns

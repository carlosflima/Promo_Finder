from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class PriceObservation:
    search_id: str
    product_key: str
    product_name: str
    site: str
    price: float
    shipping: float = 0.0
    seller: Optional[str] = None
    promotional: bool = False
    promotion_description: Optional[str] = None
    observed_at: datetime = datetime.min

    @property
    def total(self) -> float:
        return round(self.price + self.shipping, 2)


@dataclass(frozen=True)
class HistoryFilter:
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    product_key: Optional[str] = None
    site: Optional[str] = None

    def matches(self, item: PriceObservation) -> bool:
        if self.date_from and item.observed_at < self.date_from:
            return False
        if self.date_to and item.observed_at > self.date_to:
            return False
        if self.product_key and item.product_key != self.product_key:
            return False
        if self.site and item.site.casefold() != self.site.casefold():
            return False
        return True

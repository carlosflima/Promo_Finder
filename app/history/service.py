from statistics import mean
from typing import Iterable, List, Optional

from .models import HistoryFilter, PriceObservation


class PriceHistoryService:
    """In-memory history service; repository persistence can be added without changing callers."""

    def __init__(self, observations: Optional[Iterable[PriceObservation]] = None):
        self._items: List[PriceObservation] = list(observations or [])

    def record(self, observation: PriceObservation) -> PriceObservation:
        if observation.price < 0 or observation.shipping < 0:
            raise ValueError("price and shipping cannot be negative")
        self._items.append(observation)
        return observation

    def search(self, history_filter: Optional[HistoryFilter] = None) -> List[PriceObservation]:
        # Empty filter intentionally returns no records: the UI must opt into history.
        if history_filter is None:
            return []
        return [item for item in self._items if history_filter.matches(item)]

    def all(self) -> List[PriceObservation]:
        return list(self._items)

    def clear(self) -> None:
        self._items.clear()

    def baseline(self, product_key: str, site: Optional[str] = None) -> Optional[float]:
        values = [x.total for x in self._items if x.product_key == product_key and (not site or x.site.casefold() == site.casefold())]
        return round(mean(values), 2) if values else None

    def promotion_score(self, observation: PriceObservation) -> Optional[float]:
        baseline = self.baseline(observation.product_key, observation.site)
        if baseline is None or baseline <= 0:
            return None
        return round((baseline - observation.total) / baseline * 100, 2)

"""Canonical shipping models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ShippingQuote:
    cep: str
    amount: Optional[float]
    free_shipping: bool = False
    available: bool = True
    provider: str = ""
    estimated_days: Optional[int] = None
    message: str = ""

    @property
    def effective_amount(self) -> float:
        if self.free_shipping or self.amount is None:
            return 0.0
        return max(0.0, self.amount)

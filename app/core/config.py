"""Environment-backed configuration for the refactored application."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "15"))
    request_delay: float = float(os.getenv("REQUEST_DELAY", "0.5"))
    max_items_per_site: int = int(os.getenv("MAX_ITEMS_PER_SITE", "5"))
    max_sites: int = int(os.getenv("MAX_SITES", "20"))
    search_workers: int = int(os.getenv("SEARCH_WORKERS", "8"))
    user_agent: str = os.getenv(
        "USER_AGENT",
        "PromoFinder/0.2 (+https://github.com/carlosflima/Promo_Finder)",
    )


settings = Settings()

"""Normalize connector payloads into the canonical SearchResult model."""
from __future__ import annotations

from typing import Any

from .models import SearchResult


def normalize_result(payload: dict[str, Any], *, source: str) -> SearchResult:
    promotional_price = payload.get("promotional_price")
    regular_price = payload.get("regular_price")
    price = promotional_price if promotional_price is not None else payload.get("price", 0)
    return SearchResult(
        site=str(payload.get("site") or source).strip(),
        title=str(payload.get("title") or payload.get("name") or "").strip(),
        price=float(price or 0),
        link=str(payload.get("link") or payload.get("url") or "").strip(),
        seller=str(payload.get("seller") or "").strip(),
        shipping=float(payload["shipping"]) if payload.get("shipping") is not None else None,
        promotional=promotional_price is not None or bool(payload.get("promotional")),
        promotion=str(payload.get("promotion") or "").strip(),
        rating=float(payload["rating"]) if payload.get("rating") is not None else None,
        seller_rating=float(payload["seller_rating"]) if payload.get("seller_rating") is not None else None,
        marketplace=bool(payload.get("marketplace")),
        store_verified=bool(payload.get("store_verified")),
        seller_verified=bool(payload.get("seller_verified")),
        metadata={"regular_price": regular_price} if regular_price is not None else {},
    )

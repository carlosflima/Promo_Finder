"""Mercado Livre API adapter.

The adapter expects a valid API endpoint/token to be supplied by configuration;
no credentials are stored in the repository.
"""
from __future__ import annotations

from typing import Any

from .http_connector import HttpConnector
from .normalizer import normalize_result


class MercadoLivreConnector:
    def __init__(self, http: HttpConnector, endpoint: str, access_token: str):
        if not access_token.strip():
            raise ValueError("access_token cannot be empty")
        self.http = http
        self.endpoint = endpoint
        self.access_token = access_token

    def search(self, query: str):
        payload = self.http.get_json(
            self.endpoint,
            params={"q": query},
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        return [self._normalize(item) for item in payload.get("results", [])]

    @staticmethod
    def _normalize(item: dict[str, Any]):
        price = item.get("price")
        original = item.get("original_price")
        promotional = bool(original is not None and price is not None and float(price) < float(original))
        payload = {
            "site": "mercadolivre.com.br",
            "title": item.get("title"),
            "price": price,
            "promotional_price": price if promotional else None,
            "regular_price": original,
            "url": item.get("permalink"),
            "seller": str(item.get("seller", {}).get("nickname", "")),
            "shipping": item.get("shipping", {}).get("cost"),
            "promotion": "Preço promocional" if promotional else "",
        }
        result = normalize_result(payload, source="mercadolivre.com.br")
        result.marketplace = True
        return result

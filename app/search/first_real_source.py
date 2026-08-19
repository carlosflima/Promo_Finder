"""Adapter factory for the first authorized real price source.

The transport/parser are injected so credentials, API endpoints and source
terms remain configuration concerns rather than hard-coded fake data.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .http_connector import HttpConnector
from .normalizer import normalize_result


class RealPriceSource:
    def __init__(self, source_domain: str, http: HttpConnector, endpoint: str, parser: Callable[[Any], list[dict[str, Any]]]):
        self.source_domain = source_domain
        self.http = http
        self.endpoint = endpoint
        self.parser = parser

    def search(self, query: str):
        payload = self.http.get_json(self.endpoint, params={"q": query})
        return [normalize_result(item, source=self.source_domain) for item in self.parser(payload)]

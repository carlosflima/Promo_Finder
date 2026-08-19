"""Common contract and safe execution wrapper for search connectors."""
from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Protocol

from .models import SearchResult


class SearchConnector(Protocol):
    def search(self, query: str) -> list[SearchResult]:
        ...


@dataclass(frozen=True)
class ConnectorResponse:
    results: list[SearchResult]
    elapsed_ms: int
    error: str | None = None


def execute_connector(connector: SearchConnector, query: str, timeout_seconds: float = 10.0) -> ConnectorResponse:
    """Execute one connector and isolate failures from the other sources.

    A synchronous connector cannot be forcefully cancelled safely here, so the
    timeout is measured and reported rather than pretending to abort its work.
    Concrete async/HTTP adapters can enforce hard network timeouts themselves.
    """
    started = monotonic()
    try:
        results = connector.search(query)
        elapsed_ms = int((monotonic() - started) * 1000)
        if elapsed_ms > timeout_seconds * 1000:
            return ConnectorResponse([], elapsed_ms, "connector timeout")
        return ConnectorResponse(results, elapsed_ms)
    except Exception as exc:  # isolate one failing source
        elapsed_ms = int((monotonic() - started) * 1000)
        return ConnectorResponse([], elapsed_ms, f"connector error: {exc}")

"""HTTP connector base with explicit timeout/retry policy."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class HttpPolicy:
    timeout_seconds: float = 8.0
    retries: int = 1


class HttpConnector:
    """Small transport abstraction; real sources provide the request function."""

    def __init__(self, request: Callable[..., Any], policy: HttpPolicy | None = None):
        self.request = request
        self.policy = policy or HttpPolicy()

    def get_json(self, url: str, **kwargs: Any) -> Any:
        last_error: Exception | None = None
        for attempt in range(self.policy.retries + 1):
            try:
                return self.request(url, timeout=self.policy.timeout_seconds, **kwargs)
            except Exception as exc:
                last_error = exc
                if attempt >= self.policy.retries:
                    raise
        raise last_error  # pragma: no cover

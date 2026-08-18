"""Select candidate sites without treating discovery as trust verification."""
from __future__ import annotations

from collections.abc import Iterable
from urllib.parse import urlparse

from .models import SearchResult


def _domain(value: str) -> str:
    parsed = urlparse(value if "://" in value else f"https://{value}")
    return (parsed.netloc or parsed.path).lower().removeprefix("www.").split(":", 1)[0]


def discover_candidate_sites(
    results: Iterable[SearchResult],
    explicit_sites: Iterable[str] = (),
    top_site_count: int = 3,
) -> list[str]:
    """Return explicit sites plus the cheapest discovered sites.

    Discovery ranks candidates by observed effective cost. Trust flags remain
    separate so a cheap but unverified source is never silently treated as
    trusted merely because it ranked well.
    """
    grouped: dict[str, list[SearchResult]] = {}
    for result in results:
        domain = _domain(result.site or result.link)
        grouped.setdefault(domain, []).append(result)

    explicit = [_domain(site) for site in explicit_sites if str(site).strip()]
    ranked = sorted(
        grouped,
        key=lambda domain: min(item.total_price for item in grouped[domain]),
    )

    output: list[str] = []
    for domain in [*explicit, *ranked]:
        if domain and domain not in output:
            output.append(domain)
        if len(output) >= max(0, top_site_count) + len(set(explicit)):
            break
    return output

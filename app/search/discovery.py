"""Discovery of candidate Brazilian shopping sites.

Discovery returns candidates only; it never treats a discovered domain as trusted
without a separate trust assessment. External search providers can be plugged in
later without changing the ranking pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from .trust import TrustAssessment, assess_site


@dataclass(frozen=True)
class SiteCandidate:
    url: str
    hostname: str
    source: str
    trust: TrustAssessment


BRAZILIAN_SHOPPING_DOMAINS = (
    "amazon.com.br",
    "mercadolivre.com.br",
    "magazineluiza.com.br",
    "carrefour.com.br",
    "kabum.com.br",
    "casasbahia.com.br",
    "pontofrio.com.br",
    "extra.com.br",
    "americanas.com.br",
    "shopee.com.br",
)


def discover_candidates(extra_urls: list[str] | None = None) -> list[SiteCandidate]:
    """Return known national domains plus explicitly supplied URLs.

    The list is deliberately bounded. A future web-search provider can append
    candidates, after which ``assess_site`` and seller/store reputation checks
    decide whether they are eligible for product searches.
    """
    urls = [f"https://{domain}" for domain in BRAZILIAN_SHOPPING_DOMAINS]
    urls.extend(extra_urls or [])
    candidates: list[SiteCandidate] = []
    seen: set[str] = set()
    for url in urls:
        assessment = assess_site(url)
        host = assessment.hostname
        if not host or host in seen:
            continue
        seen.add(host)
        candidates.append(SiteCandidate(assessment.url, host, "catalog" if not extra_urls or url not in extra_urls else "user", assessment))
    return candidates


def approved_candidates(extra_urls: list[str] | None = None) -> list[SiteCandidate]:
    return [candidate for candidate in discover_candidates(extra_urls) if candidate.trust.approved]

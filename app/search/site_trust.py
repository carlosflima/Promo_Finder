"""Deterministic provenance signals for discovered shopping sites."""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class SiteTrust:
    domain: str
    https: bool
    has_product_url: bool
    score: int
    trusted: bool


def assess_site(url: str, *, has_product_url: bool = True) -> SiteTrust:
    value = url.strip()
    parsed = urlparse(value if "://" in value else f"https://{value}")
    domain = (parsed.netloc or parsed.path).lower().removeprefix("www.").split(":", 1)[0]
    https = parsed.scheme == "https"
    score = (60 if https else 0) + (40 if has_product_url else 0)
    return SiteTrust(domain=domain, https=https, has_product_url=has_product_url, score=score, trusted=score >= 60)

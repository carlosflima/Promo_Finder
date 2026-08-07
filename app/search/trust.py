"""Trust and provenance helpers for discovered/custom stores.

This module is intentionally conservative: it does not claim a store is safe merely
because it responds to HTTP. It produces a transparent score from observable signals
and leaves final approval to the caller/configuration.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class TrustAssessment:
    url: str
    hostname: str
    https: bool
    score: int
    approved: bool
    reasons: tuple[str, ...]


def assess_site(url: str, *, min_score: int = 60) -> TrustAssessment:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower().strip(".")
    reasons: list[str] = []
    score = 0

    if parsed.scheme == "https":
        score += 30
        reasons.append("HTTPS")
    elif parsed.scheme == "http":
        reasons.append("HTTP sem TLS")
    else:
        reasons.append("esquema inválido")

    if host.endswith(".br"):
        score += 20
        reasons.append("domínio .br")

    if host and not _is_private_or_local(host):
        score += 20
        reasons.append("host público")
    else:
        reasons.append("host local/privado")

    # Presence of a registrable-looking hostname is a weak signal only.
    if "." in host and len(host) >= 4:
        score += 10
        reasons.append("hostname válido")

    approved = parsed.scheme == "https" and score >= min_score and not _is_private_or_local(host)
    return TrustAssessment(parsed.geturl(), host, parsed.scheme == "https", score, approved, tuple(reasons))


def _is_private_or_local(host: str) -> bool:
    import ipaddress

    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        return True
    try:
        return ipaddress.ip_address(host).is_private
    except ValueError:
        return False

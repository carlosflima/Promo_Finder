"""Site configuration and URL validation for user-supplied stores."""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


ALLOWED_SCHEMES = {"http", "https"}
BLOCKED_HOST_PARTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}


@dataclass(frozen=True)
class SiteConfig:
    url: str
    name: str = ""
    enabled: bool = True
    trusted: bool = False

    @property
    def host(self) -> str:
        return urlparse(self.url).netloc.lower().split(":", 1)[0]


def validate_site_url(value: str) -> str:
    """Validate and normalize a user-provided HTTP(S) site URL."""
    raw = (value or "").strip()
    if not raw:
        raise ValueError("Informe uma URL de site.")
    if "://" not in raw:
        raw = "https://" + raw
    parsed = urlparse(raw)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES or not parsed.netloc:
        raise ValueError("A URL deve usar http:// ou https:// e possuir um domínio válido.")
    host = parsed.hostname or ""
    if host.lower() in BLOCKED_HOST_PARTS:
        raise ValueError("Host local não é permitido para pesquisa externa.")
    return f"{parsed.scheme.lower()}://{parsed.netloc}{parsed.path.rstrip('/') or ''}"


def site_name(url: str) -> str:
    host = urlparse(validate_site_url(url)).hostname or ""
    return host.removeprefix("www.")

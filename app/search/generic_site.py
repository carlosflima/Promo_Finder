"""Generic HTTP site search adapter.

This adapter is intentionally conservative: it only searches a user-approved
site URL and extracts ordinary product links/prices from HTML. It does not
attempt to bypass robots, authentication, CAPTCHAs or anti-bot controls.
"""
from __future__ import annotations

import re
from urllib.parse import quote_plus, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .models import SearchQuery, SearchResult
from .plugin import SearchPlugin
from .site import SiteConfig, site_name, validate_site_url

_PRICE_RE = re.compile(r"(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2}|\d+(?:[.,]\d{2})?)")


class GenericSitePlugin(SearchPlugin):
    """Best-effort connector for stores with a conventional search page."""

    def __init__(self, site: SiteConfig, timeout: float = 8.0):
        self.site = SiteConfig(validate_site_url(site.url), site.name, site.enabled, site.trusted)
        self.timeout = timeout
        self.name = site.name.strip() or site_name(self.site.url)

    def search(self, query: SearchQuery) -> list[SearchResult]:
        if not self.site.enabled:
            return []
        url = self._search_url(query.term)
        headers = {"User-Agent": "PromoFinder/0.2 (+price-comparison; contact site-owner)"}
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return self._parse(response.text, response.url, query)

    def _search_url(self, term: str) -> str:
        base = self.site.url.rstrip("/")
        # Common search conventions. The first is the least surprising for
        # generic stores; custom plugins can override this behavior later.
        return f"{base}/busca?q={quote_plus(term)}"

    def _parse(self, html: str, page_url: str, query: SearchQuery) -> list[SearchResult]:
        soup = BeautifulSoup(html, "lxml")
        results: list[SearchResult] = []
        for anchor in soup.select("a[href]"):
            title = " ".join(anchor.stripped_strings).strip()
            if len(title) < 4:
                continue
            text = " ".join(anchor.parent.stripped_strings)
            match = _PRICE_RE.search(text)
            if not match:
                continue
            price = self._money(match.group(1))
            if price is None or price <= 0:
                continue
            link = urljoin(page_url, anchor.get("href", ""))
            if urlparse(link).netloc != urlparse(page_url).netloc:
                continue
            results.append(SearchResult(title=title[:240], price=price, site=self.name, link=link))
            if len(results) >= 5:
                break
        return results

    @staticmethod
    def _money(value: str) -> float | None:
        try:
            normalized = value.replace(".", "").replace(",", ".") if "," in value else value.replace(",", "")
            return float(normalized)
        except ValueError:
            return None

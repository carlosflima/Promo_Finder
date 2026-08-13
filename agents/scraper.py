# -*- coding: utf-8 -*-
"""Motor de coleta de promoções e pesquisa genérica por termo."""
from __future__ import annotations

import hashlib
import re
import time
from dataclasses import asdict, dataclass
from typing import Optional
from urllib.parse import quote_plus, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config import MAX_ITEMS_PER_SITE, REQUEST_DELAY, REQUEST_TIMEOUT, USER_AGENT
from agents.categorizer import categorize


@dataclass
class Product:
    id: str
    title: str
    price: float
    original_price: Optional[float] = None
    discount_percent: float = 0.0
    store: str = ""
    site: str = ""
    link: str = ""
    image: str = ""
    installment: str = ""
    shipping: str = ""
    coupon_code: str = ""
    category: str = "Outros"
    seller: str = ""
    shipping_cost: float = 0.0
    promotional: bool = False
    promotion_description: str = ""

    def to_dict(self):
        return asdict(self)


def parse_price(raw: str) -> Optional[float]:
    if raw is None:
        return None
    text = re.sub(r"[^0-9,.]", "", str(raw))
    if not text:
        return None
    try:
        if "," in text and "." in text:
            text = text.replace(".", "").replace(",", ".")
        elif "," in text:
            text = text.replace(",", ".")
        return float(text)
    except ValueError:
        return None


def slugify_id(*parts) -> str:
    value = "|".join(str(p or "") for p in parts)
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def _domain_to_store_name(url: str) -> str:
    host = urlparse(url).netloc.lower().split(":")[0]
    host = host.removeprefix("www.")
    return host.split(".")[0].replace("-", " ").title()


def _request(url: str):
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.7"}
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response


def _extract_generic_cards(html: str, base_url: str, site_name: str):
    soup = BeautifulSoup(html, "lxml")
    products = []
    selectors = ["article", ".product", ".product-card", ".offer", ".deal", "[data-testid*='product']"]
    cards = []
    for selector in selectors:
        cards.extend(soup.select(selector))
        if len(cards) >= MAX_ITEMS_PER_SITE:
            break
    seen = set()
    for card in cards[:MAX_ITEMS_PER_SITE]:
        title_el = card.select_one("h1,h2,h3,h4,.title,.product-title,[data-testid*='title']")
        link_el = card.select_one("a[href]")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(" ", strip=True)
        href = urljoin(base_url, link_el.get("href", ""))
        price = None
        for el in card.select(".price,[class*='price'],[data-testid*='price']"):
            price = parse_price(el.get_text(" ", strip=True))
            if price is not None:
                break
        if not title or price is None or href in seen:
            continue
        seen.add(href)
        products.append({"title": title, "price": price, "link": href, "store": _domain_to_store_name(href), "site": site_name})
    return products


class BaseAgent:
    name = "Fonte"
    url = ""
    def search(self) -> list[dict]:
        raise NotImplementedError


class UrlAgent(BaseAgent):
    def __init__(self, name: str, url: str, term: str = ""):
        self.name = name
        self.url = url
        self.term = term.strip()

    def _candidate_urls(self):
        if not self.term:
            return [self.url]
        encoded = quote_plus(self.term)
        base = self.url.rstrip("/")
        return [f"{base}/search?q={encoded}", f"{base}/busca?q={encoded}", f"{base}?q={encoded}"]

    def search(self):
        for candidate in self._candidate_urls():
            try:
                response = _request(candidate)
                products = _extract_generic_cards(response.text, candidate, self.name)
                if products:
                    return products[:MAX_ITEMS_PER_SITE]
            except requests.RequestException:
                continue
        time.sleep(REQUEST_DELAY)
        return []


class PromobitAgent(UrlAgent):
    def __init__(self, term=""): super().__init__("Promobit", "https://www.promobit.com.br/ofertas", term)
class PelandoAgent(UrlAgent):
    def __init__(self, term=""): super().__init__("Pelando", "https://www.pelando.com.br/recentes", term)
class ZoomAgent(UrlAgent):
    def __init__(self, term=""): super().__init__("Zoom", "https://www.zoom.com.br", term)
class BuscapeAgent(UrlAgent):
    def __init__(self, term=""): super().__init__("Buscapé", "https://www.buscape.com.br", term)
class AmazonOfertasAgent(UrlAgent):
    def __init__(self, term=""): super().__init__("Amazon Brasil", "https://www.amazon.com.br/gp/goldbox", term)
class MagazineLuizaOfertasAgent(UrlAgent):
    def __init__(self, term=""): super().__init__("Magazine Luiza", "https://www.magazineluiza.com.br", term)
class CasasBahiaOfertasAgent(UrlAgent):
    def __init__(self, term=""): super().__init__("Casas Bahia", "https://www.casasbahia.com.br", term)
class KabumOfertasAgent(UrlAgent):
    def __init__(self, term=""): super().__init__("KaBuM!", "https://www.kabum.com.br", term)

AGENT_FACTORIES = [PromobitAgent, PelandoAgent, ZoomAgent, BuscapeAgent, AmazonOfertasAgent, MagazineLuizaOfertasAgent, CasasBahiaOfertasAgent, KabumOfertasAgent]


def normalize_item(raw: dict) -> Optional[Product]:
    title = str(raw.get("title") or "").strip()
    price = parse_price(raw.get("price")) if not isinstance(raw.get("price"), (int, float)) else float(raw["price"])
    if not title or price is None or price <= 0:
        return None
    original = raw.get("original_price")
    original = parse_price(original) if original and not isinstance(original, (int, float)) else original
    discount = round((1 - price / original) * 100, 1) if original and original > price else 0.0
    return Product(id=raw.get("id") or slugify_id(title, raw.get("link"), price), title=title, price=price,
        original_price=original, discount_percent=discount, store=raw.get("store") or _domain_to_store_name(raw.get("link", "")),
        site=raw.get("site") or "", link=raw.get("link") or "", image=raw.get("image") or "",
        installment=raw.get("installment") or "", shipping=raw.get("shipping") or "", coupon_code=raw.get("coupon_code") or "",
        category=raw.get("category") or categorize(title), seller=raw.get("seller") or "",
        shipping_cost=float(raw.get("shipping_cost") or 0), promotional=bool(raw.get("promotional") or discount > 0),
        promotion_description=raw.get("promotion_description") or "")


def _sample_data():
    samples = [{"title": "Smart TV 4K 55 polegadas", "price": 2499.90, "original_price": 3199.90, "store": "Oferta demonstrativa", "site": "Fallback"},
               {"title": "Notebook Intel Core i5 16GB", "price": 2899.00, "original_price": 3499.00, "store": "Oferta demonstrativa", "site": "Fallback"}]
    return [p.to_dict() for p in (normalize_item(x) for x in samples) if p]


def run_agents(term="", custom_sites=None) -> list[dict]:
    agents = [factory(term) for factory in AGENT_FACTORIES]
    for site in custom_sites or []:
        if isinstance(site, dict):
            name, url = site.get("name") or _domain_to_store_name(site.get("url", "")), site.get("url", "")
        else:
            url, name = str(site), _domain_to_store_name(str(site))
        if url:
            agents.append(UrlAgent(name, url, term))
    results, seen = [], set()
    for agent in agents:
        try:
            for raw in agent.search():
                item = normalize_item(raw)
                if not item or item.link in seen:
                    continue
                seen.add(item.link); results.append(item.to_dict())
        except Exception:
            continue
    return results or _sample_data()


def run_all_agents() -> list[dict]:
    return run_agents()


def filter_by_discount(products: list[dict], min_discount: int = 25, ignore_discount: bool = False):
    if ignore_discount:
        return products
    return [p for p in products if float(p.get("discount_percent", 0) or 0) >= min_discount]

# -*- coding: utf-8 -*-
"""Motor inicial de coleta de promoções.

A primeira versão mantém adaptadores independentes para fontes públicas e
um fallback local para que a interface permaneça utilizável quando uma
fonte bloquear requisições automatizadas.
"""
from __future__ import annotations

import hashlib
import re
import time
from dataclasses import asdict, dataclass
from typing import Optional
from urllib.parse import urljoin, urlparse

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

    def to_dict(self):
        return asdict(self)


def parse_price(raw: str) -> Optional[float]:
    if not raw:
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
    selectors = [
        "article", ".product", ".product-card", ".offer", ".deal", "[data-testid*='product']",
    ]
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
        products.append({
            "title": title, "price": price, "link": href,
            "store": _domain_to_store_name(href), "site": site_name,
        })
    return products


class BaseAgent:
    name = "Fonte"
    url = ""

    def search(self) -> list[dict]:
        raise NotImplementedError


class UrlAgent(BaseAgent):
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def search(self):
        try:
            response = _request(self.url)
            return _extract_generic_cards(response.text, self.url, self.name)
        except requests.RequestException:
            return []
        finally:
            time.sleep(REQUEST_DELAY)


class PromobitAgent(UrlAgent):
    def __init__(self):
        super().__init__("Promobit", "https://www.promobit.com.br/ofertas/")


class PelandoAgent(UrlAgent):
    def __init__(self):
        super().__init__("Pelando", "https://www.pelando.com.br/recentes")


class ZoomAgent(UrlAgent):
    def __init__(self):
        super().__init__("Zoom", "https://www.zoom.com.br")


class BuscapeAgent(UrlAgent):
    def __init__(self):
        super().__init__("Buscapé", "https://www.buscape.com.br")


class AmazonOfertasAgent(UrlAgent):
    def __init__(self):
        super().__init__("Amazon Brasil", "https://www.amazon.com.br/gp/goldbox")


class MagazineLuizaOfertasAgent(UrlAgent):
    def __init__(self):
        super().__init__("Magazine Luiza", "https://www.magazineluiza.com.br")


class CasasBahiaOfertasAgent(UrlAgent):
    def __init__(self):
        super().__init__("Casas Bahia", "https://www.casasbahia.com.br")


class KabumOfertasAgent(UrlAgent):
    def __init__(self):
        super().__init__("KaBuM!", "https://www.kabum.com.br")


AGENTS = [
    PromobitAgent(), PelandoAgent(), ZoomAgent(), BuscapeAgent(),
    AmazonOfertasAgent(), MagazineLuizaOfertasAgent(), CasasBahiaOfertasAgent(), KabumOfertasAgent(),
]


def normalize_item(raw: dict) -> Optional[Product]:
    title = str(raw.get("title") or "").strip()
    price = parse_price(raw.get("price")) if not isinstance(raw.get("price"), (int, float)) else float(raw["price"])
    if not title or price is None or price <= 0:
        return None
    original = raw.get("original_price")
    original = parse_price(original) if original and not isinstance(original, (int, float)) else original
    discount = 0.0
    if original and original > price:
        discount = round((1 - price / original) * 100, 1)
    product = Product(
        id=raw.get("id") or slugify_id(title, raw.get("link"), price),
        title=title,
        price=price,
        original_price=original,
        discount_percent=discount,
        store=raw.get("store") or _domain_to_store_name(raw.get("link", "")),
        site=raw.get("site") or "",
        link=raw.get("link") or "",
        image=raw.get("image") or "",
        installment=raw.get("installment") or "",
        shipping=raw.get("shipping") or "",
        coupon_code=raw.get("coupon_code") or "",
        category=raw.get("category") or categorize(title),
    )
    return product


def _sample_data():
    samples = [
        {"title": "Smart TV 4K 55 polegadas", "price": 2499.90, "original_price": 3199.90, "store": "Oferta demonstrativa", "site": "Fallback"},
        {"title": "Notebook Intel Core i5 16GB", "price": 2899.00, "original_price": 3499.00, "store": "Oferta demonstrativa", "site": "Fallback"},
    ]
    return [normalize_item(item).to_dict() for item in samples if normalize_item(item)]


def run_all_agents() -> list[dict]:
    results = []
    seen = set()
    for agent in AGENTS:
        try:
            for raw in agent.search():
                item = normalize_item(raw)
                if not item or item.link in seen:
                    continue
                seen.add(item.link)
                results.append(item.to_dict())
        except Exception:
            continue
    return results or _sample_data()


def filter_by_discount(products: list[dict], min_discount: int = 25, ignore_discount: bool = False):
    if ignore_discount:
        return products
    return [p for p in products if float(p.get("discount_percent", 0) or 0) >= min_discount]

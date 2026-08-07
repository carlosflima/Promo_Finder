# -*- coding: utf-8 -*-
"""Classificação automática de produtos por palavras-chave."""
import unicodedata
from config import CATEGORY_KEYWORDS, DEFAULT_CATEGORY


def _normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def categorize(title: str) -> str:
    if not title:
        return DEFAULT_CATEGORY
    normalized_title = _normalize(title)
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(_normalize(kw) in normalized_title for kw in keywords):
            return category
    return DEFAULT_CATEGORY

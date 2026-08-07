"""Product term normalization used before dispatching searches."""
from __future__ import annotations

import re
import unicodedata


def normalize_term(term: str) -> str:
    text = unicodedata.normalize("NFKD", term or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^\w\s-]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def search_terms(term: str) -> list[str]:
    normalized = normalize_term(term)
    if not normalized:
        return []
    terms = [normalized]
    compact = re.sub(r"\s+", " ", normalized)
    if compact.lower() != normalized.lower():
        terms.append(compact)
    return list(dict.fromkeys(terms))

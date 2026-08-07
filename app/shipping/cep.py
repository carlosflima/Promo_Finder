"""Brazilian CEP normalization and validation.

This module validates the shape of a CEP locally. It intentionally does not
claim that a CEP exists or that a store delivers to it; those are provider- or
store-specific checks handled by the shipping adapters.
"""
from __future__ import annotations

import re

_CEP_RE = re.compile(r"^\d{8}$")


def normalize_cep(value: str) -> str:
    """Return an eight-digit CEP, accepting ``00000-000`` input."""
    digits = re.sub(r"\D", "", value or "")
    if not _CEP_RE.fullmatch(digits):
        raise ValueError("CEP inválido. Informe 8 dígitos, por exemplo 01001-000.")
    return digits


def format_cep(value: str) -> str:
    digits = normalize_cep(value)
    return f"{digits[:5]}-{digits[5:]}"

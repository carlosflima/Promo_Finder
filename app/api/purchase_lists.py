"""HTTP helpers for purchase-list persistence.

The functions are intentionally framework-agnostic so Flask can be wired in
without moving business rules into the route layer.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.repository.purchase_list_repository import PurchaseListRepository


def create_list(name: str, repository: PurchaseListRepository) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    data = {"id": str(uuid4()), "name": name.strip() or "Lista de compras", "items": [], "created_at": now, "updated_at": now}
    repository.save(data)
    return data


def delete_list(list_id: str, repository: PurchaseListRepository) -> bool:
    return repository.delete(list_id)

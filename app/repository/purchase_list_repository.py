"""SQLite persistence for purchase lists."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class PurchaseListRepository:
    def __init__(self, database_path: str | Path = "data/promo_finder.db") -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS purchase_lists (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    items_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

    def save(self, data: dict[str, Any]) -> None:
        with self._connect() as db:
            db.execute(
                """INSERT INTO purchase_lists(id,name,items_json,created_at,updated_at)
                   VALUES(?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET name=excluded.name,
                   items_json=excluded.items_json, updated_at=excluded.updated_at""",
                (data["id"], data["name"], json.dumps(data["items"], ensure_ascii=False), data["created_at"], data["updated_at"]),
            )

    def get(self, list_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM purchase_lists WHERE id=?", (list_id,)).fetchone()
        if not row:
            return None
        return {"id": row["id"], "name": row["name"], "items": json.loads(row["items_json"]), "created_at": row["created_at"], "updated_at": row["updated_at"]}

    def list_all(self) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM purchase_lists ORDER BY updated_at DESC").fetchall()
        return [{"id": r["id"], "name": r["name"], "items": json.loads(r["items_json"]), "created_at": r["created_at"], "updated_at": r["updated_at"]} for r in rows]

    def delete(self, list_id: str) -> bool:
        with self._connect() as db:
            result = db.execute("DELETE FROM purchase_lists WHERE id=?", (list_id,))
        return result.rowcount > 0

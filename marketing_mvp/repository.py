from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class CampaignRepository:
    def __init__(self, path: str | Path = "data/campaigns.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS campaigns (
                    campaign_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def save(self, campaign: dict[str, Any]) -> None:
        payload = json.dumps(campaign, ensure_ascii=False)
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO campaigns(campaign_id, payload) VALUES (?, ?)
                ON CONFLICT(campaign_id) DO UPDATE SET
                payload=excluded.payload, updated_at=CURRENT_TIMESTAMP""",
                (campaign["campaign_id"], payload),
            )

    def load(self, campaign_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload FROM campaigns WHERE campaign_id = ?", (campaign_id,)
            ).fetchone()
        return json.loads(row[0]) if row else None


from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol, Any


class CapaService(Protocol):
    def check(self, start_date: str, end_date: str, target_capa: int) -> dict[str, Any]: ...


class MockCapaService:
    def __init__(self, path: str | Path = "data/mock_capa.json") -> None:
        self.rows = json.loads(Path(path).read_text(encoding="utf-8"))

    def check(self, start_date: str, end_date: str, target_capa: int) -> dict[str, Any]:
        matching = [
            row for row in self.rows
            if row["start_date"] <= start_date and row["end_date"] >= end_date
        ]
        if matching:
            available = max(row["available_capa"] for row in matching)
        else:
            available = min((row["available_capa"] for row in self.rows), default=0)
        alternatives = sorted(
            [row for row in self.rows if row["available_capa"] >= target_capa],
            key=lambda row: row["start_date"],
        )[:3]
        return {
            "available_capa": available,
            "is_possible": available >= target_capa,
            "shortfall": max(target_capa - available, 0),
            "alternatives": alternatives,
            "source": "mock",
        }


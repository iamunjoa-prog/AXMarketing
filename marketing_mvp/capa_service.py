from __future__ import annotations

import csv
import io
import json
import ssl
from datetime import date, datetime
from pathlib import Path
from typing import Any, Protocol
from urllib.request import Request, urlopen

try:
    import truststore
except ImportError:  # pragma: no cover - fallback for minimal environments
    truststore = None


DEFAULT_CAPA_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1DdmCQd8jPuWp3Z6NmM3yRHGx4Cc7XhxXEhnpJUD6hpE/"
    "gviz/tq?tqx=out:csv&gid=361329742"
)


class CapaService(Protocol):
    def check(
        self,
        start_date: str,
        end_date: str,
        target_capa: int,
        capacity_type: str = "coupon",
    ) -> dict[str, Any]: ...


def _parse_sheet_date(value: str) -> date:
    return datetime.strptime(value.strip(), "%Y. %m. %d").date()


class GoogleSheetCapaService:
    """Read the latest daily capacity from the campaign schedule sheet."""

    def __init__(self, csv_url: str = DEFAULT_CAPA_SHEET_CSV_URL, timeout: int = 8) -> None:
        self.csv_url = csv_url
        self.timeout = timeout

    def _ssl_context(self) -> ssl.SSLContext:
        if truststore is not None:
            return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        return ssl.create_default_context()

    def _rows(self) -> list[dict[str, str]]:
        request = Request(self.csv_url, headers={"User-Agent": "AX-Marketing-Manager/1.0"})
        with urlopen(
            request,
            timeout=self.timeout,
            context=self._ssl_context(),
        ) as response:
            payload = response.read().decode("utf-8-sig")
        return list(csv.DictReader(io.StringIO(payload)))

    def check(
        self,
        start_date: str,
        end_date: str,
        target_capa: int,
        capacity_type: str = "coupon",
    ) -> dict[str, Any]:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        matching = [
            row for row in self._rows()
            if start <= _parse_sheet_date(row["날짜"]) <= end
        ]
        if not matching:
            raise ValueError("선택한 기간의 Capa 데이터가 Google Sheet에 없습니다.")

        daily = [
            {
                "date": _parse_sheet_date(row["날짜"]).isoformat(),
                "banner_available": int(row["배너 잔여 슬롯"].replace(",", "") or 0),
                "coupon_available": int(row["쿠폰 잔여 슬롯"].replace(",", "") or 0),
            }
            for row in matching
        ]
        expected_days = (end - start).days + 1
        minimum_banner = min(row["banner_available"] for row in daily)
        minimum_coupon = min(row["coupon_available"] for row in daily)
        if capacity_type == "both":
            available = min(minimum_banner, minimum_coupon)
            capacity_label = "배너·쿠폰 잔여 슬롯"
        elif capacity_type == "coupon":
            available = minimum_coupon
            capacity_label = "쿠폰 잔여 슬롯"
        else:
            available = minimum_banner
            capacity_label = "배너 잔여 슬롯"
        return {
            "available_capa": available,
            "is_possible": available >= target_capa and len(daily) == expected_days,
            "shortfall": max(target_capa - available, 0),
            "alternatives": [],
            "source": "google_sheet_live",
            "capacity_type": capacity_type,
            "capacity_label": capacity_label,
            "minimum_banner_available": minimum_banner,
            "minimum_coupon_available": minimum_coupon,
            "covered_days": len(daily),
            "expected_days": expected_days,
            "daily": daily,
        }


class MockCapaService:
    def __init__(self, path: str | Path = "data/mock_capa.json") -> None:
        self.rows = json.loads(Path(path).read_text(encoding="utf-8"))

    def check(
        self,
        start_date: str,
        end_date: str,
        target_capa: int,
        capacity_type: str = "coupon",
    ) -> dict[str, Any]:
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
            "capacity_type": capacity_type,
        }

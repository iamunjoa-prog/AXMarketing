from __future__ import annotations

from datetime import date, timedelta
from typing import Any


EVENT_TYPE_SOURCE = (
    "B tv 이벤트 유형",
    "https://docs.google.com/spreadsheets/d/"
    "1W5q5-zgAqOuXBxT3KKS7tiqJsFcRIxlbWaCWJiU99XQ/edit?gid=1283879544",
)
MONTHLY_SOURCE = (
    "4.2 마케팅 인사이트_방송 월정액",
    "https://docs.google.com/document/d/"
    "1degwwbuvxmHwOebOJzad6XyATQXt5VPjb7PDtRfpcLc/edit",
)
BTV_PLUS_SOURCE = (
    "4.3 - 마케팅 인사이트 (B tv+)",
    "https://docs.google.com/document/d/"
    "1NgT6MSNO-mK-CzrdhVF9ScDyiLrQ8m4qHjkjweTk4vg/edit",
)
OPERATIONS_SOURCE = (
    "AX Marketing 운영·Capa 시트",
    "https://docs.google.com/spreadsheets/d/"
    "1DdmCQd8jPuWp3Z6NmM3yRHGx4Cc7XhxXEhnpJUD6hpE/edit?gid=339825338",
)


def is_btv_plus_product(product_name: str) -> bool:
    normalized = product_name.lower().replace(" ", "")
    return "btv+" in normalized


def _includes_weekend(start_value: str, end_value: str) -> bool | None:
    if not start_value or not end_value:
        return None
    try:
        current = date.fromisoformat(start_value)
        end = date.fromisoformat(end_value)
    except ValueError:
        return None
    if current > end:
        return None
    while current <= end:
        if current.weekday() >= 5:
            return True
        current += timedelta(days=1)
    return False


def assess_ppm_campaign(campaign: dict[str, Any]) -> dict[str, Any]:
    """Return the PPM knowledge track without replacing confirmed facts."""
    if campaign.get("product_type") != "PPM":
        return {
            "applies": False,
            "track": "",
            "sources": [],
            "guidance": "",
            "recommendation": "",
            "caution": "",
        }

    product_name = campaign.get("product_name") or "방송 월정액"
    benefit = (campaign.get("benefit") or "").strip()
    is_btv_plus = is_btv_plus_product(product_name)
    sources = [EVENT_TYPE_SOURCE, MONTHLY_SOURCE]
    track = "B tv+ 특화 PPM" if is_btv_plus else "방송 월정액 PPM"
    if is_btv_plus:
        sources.append(BTV_PLUS_SOURCE)

    guidance_parts = [
        "사용자가 확정한 가입 조건과 할인율을 바꾸지 않고, 상품명·가입 조건·혜택 기간을 분리해 명확히 씁니다."
    ]
    if "CJ ENM" in product_name.upper():
        guidance_parts.append(
            "CJ ENM 월정액은 미가입 고객의 신규 전환과 해지 고객의 윈백을 구분해 메시지를 설계합니다."
        )
    if benefit and benefit != "혜택 없음":
        guidance_parts.append(
            f"현재 확정 혜택은 ‘{benefit}’이며 이 값을 카피 기준으로 사용합니다."
        )

    recommendations: list[str] = []
    target_capa = int(campaign.get("target_capa") or 0)
    if is_btv_plus and target_capa:
        if target_capa >= 1_000_000:
            recommendations.append(
                "대규모 신규 유입 목적이면 FOD·PPV·실시간 이용군을 우선 검토합니다."
            )
        elif 200_000 <= target_capa <= 300_000:
            recommendations.append(
                "가입률과 매출 효율 목적이면 PPM 유료 경험군을 우선 검토합니다."
            )
        elif target_capa <= 50_000:
            recommendations.append(
                "소규모 파일럿이면 PPM 무료 경험군을 우선 검토합니다."
            )
    weekend = _includes_weekend(
        campaign.get("start_date") or "",
        campaign.get("end_date") or "",
    )
    if is_btv_plus and weekend is False:
        recommendations.append(
            "B tv+ 과거 운영 가이드상 가능하면 기간에 주말을 포함하는 안을 검토합니다."
        )
    elif is_btv_plus and weekend is True:
        recommendations.append(
            "현재 일정에는 B tv+ 가이드가 권장하는 주말이 포함되어 있습니다."
        )

    return {
        "applies": True,
        "track": track,
        "sources": sources,
        "guidance": " ".join(guidance_parts),
        "operations_source": OPERATIONS_SOURCE,
        "recommendation": " ".join(recommendations),
        "caution": (
            "과거 성과 수치는 현재 성과를 보장하지 않습니다. 최신 타겟 모수와 구좌 가용성, "
            "할인 종료 후 운영 조건을 확정한 뒤 사용해야 합니다."
        ),
    }

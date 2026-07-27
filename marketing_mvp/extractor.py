from __future__ import annotations

import re
from datetime import date
from typing import Any


def extract_reference_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s<>]+", text)


def _number(text: str) -> int:
    clean = text.replace(",", "").strip()
    match = re.match(r"(\d+(?:\.\d+)?)\s*(만|천)?", clean)
    if not match:
        return 0
    value = float(match.group(1))
    unit = match.group(2)
    multiplier = 10_000 if unit == "만" else 1_000 if unit == "천" else 1
    return int(value * multiplier)


def _iso(year: int, month: int, day: int) -> str:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return ""


def extract_fields(text: str, today: date | None = None) -> dict[str, Any]:
    """Extract only explicitly supplied values; never overwrite with guesses."""
    today = today or date.today()
    result: dict[str, Any] = {}

    both_pending = re.search(
        r"(?:일정|기간|일자)\s*(?:과|와|,|·)\s*(?:혜택|리워드|보상).{0,8}(?:미정|나중|추후)",
        text,
    )
    if both_pending or re.search(r"(?:일정|기간|일자).{0,6}(?:미정|나중|추후)", text):
        result["schedule_pending"] = True
    if both_pending or re.search(r"(?:혜택|리워드|보상).{0,6}(?:미정|나중|추후)", text):
        result["benefit_pending"] = True
    if re.search(r"(?:혜택|리워드|보상)(?:은|는|이|가)?\s*(?:없음|없어|없다|없습니다)", text):
        result["benefit"] = "혜택 없음"
        result["benefit_pending"] = False
    is_raffle_benefit = (
        "추첨" in text
        and re.search(r"(?:증정|경품|지급|제공)", text)
    )
    if is_raffle_benefit:
        result["benefit"] = text.strip().rstrip(".。")
        result["benefit_pending"] = False
    purchase_match = re.search(r"(?:구매|참여|응모)", text)
    is_point_benefit = (
        purchase_match
        and re.search(r"\d[\d,]*\s*(?:원|P|포인트)", text, re.IGNORECASE)
        and re.search(r"(?:포인트|증정|지급|적립|백)", text, re.IGNORECASE)
    )
    if is_point_benefit and not is_raffle_benefit:
        result["benefit"] = text[purchase_match.start():].strip().rstrip(".。")
        result["benefit_pending"] = False

    is_subscription_discount = (
        re.search(r"(?:신규\s*가입|가입\s*시|첫\s*달|\d+\s*개월)", text)
        and re.search(r"(?:\d+\s*%|[\d,]+\s*원|무료)", text)
        and re.search(r"(?:할인|무료)", text)
    )
    if is_subscription_discount and not result.get("benefit"):
        result["benefit"] = text.strip().rstrip(".。")
        result["benefit_pending"] = False

    audience = re.search(r"(?<![A-Za-z])(MASS|TARGET)(?![A-Za-z])", text, re.IGNORECASE)
    if audience:
        result["audience_type"] = audience.group(1).upper()

    is_ppm = (
        re.search(r"(?<![A-Za-z])PPM(?![A-Za-z])", text, re.IGNORECASE)
        or "월정액" in text
        or re.search(r"(?<![A-Za-z])B\s*tv\s*\+", text, re.IGNORECASE)
    )
    is_ppv = re.search(r"(?<![A-Za-z])PPV(?![A-Za-z])", text, re.IGNORECASE)
    if is_ppm:
        result["product_type"] = "PPM"
        result["product_category"] = "월정액"
    elif is_ppv:
        result["product_type"] = "PPV"

    capa = re.search(r"(?:목표\s*)?(?:capa|모수)\s*(?:는|은|:)?\s*([\d,.]+\s*(?:만|천)?)", text, re.IGNORECASE)
    if capa:
        result["target_capa"] = _number(capa.group(1))

    benefit_patterns = [
        r"((?:구매|참여|응모)(?:하면|할\s*때|한\s*고객|고객)?[^,.。\n]{0,40}?"
        r"(?:추첨)[^,.。\n]{0,40}?(?:증정|지급|제공)"
        r"(?:\s*\([^)]*(?:명|인)[^)]*\))?)",
        r"((?:구매|참여|응모)\s*(?:시|하면|할\s*때)\s*[\d,]+\s*(?:P|포인트|원)\s*(?:백|지급|증정|제공|적립)?)",
        r"((?:구매|참여|응모)(?:하면|시)?\s*[\d,]+\s*(?:P|포인트|원)(?:백|지급|증정|제공|적립)?)",
        r"(혜택\s*(?:은|는|:)?\s*[^,.。\n]+)",
        r"(리워드\s*(?:은|는|:)?\s*[^,.。\n]+)",
    ]
    if not result.get("benefit_pending") and not result.get("benefit"):
        for pattern in benefit_patterns:
            benefit = re.search(pattern, text, re.IGNORECASE)
            if benefit:
                result["benefit"] = re.sub(
                    r"^(?:혜택|리워드)\s*(?:은|는|:)?\s*",
                    "",
                    benefit.group(1),
                ).strip()
                break

    full_range = re.search(
        r"(?:(\d{4})년?\s*)?(\d{1,2})월\s*(\d{1,2})일?\s*(?:부터|~|-)\s*"
        r"(?:(\d{4})년?\s*)?(?:(\d{1,2})월\s*)?(\d{1,2})일",
        text,
    )
    slash_range = re.search(
        r"(?:(\d{4})[./-])?(\d{1,2})[./-](\d{1,2})\s*(?:부터|~)\s*"
        r"(?:(\d{4})[./-])?(\d{1,2})[./-](\d{1,2})",
        text,
    )
    match = full_range or slash_range
    has_schedule_flexibility = re.search(
        r"(?:1\s*주일|일주일|단축|조정|변경|봐서|상황\s*보고)",
        text,
    )
    if match:
        y1 = int(match.group(1) or today.year)
        m1, d1 = int(match.group(2)), int(match.group(3))
        y2 = int(match.group(4) or y1)
        m2 = int(match.group(5) or m1)
        d2 = int(match.group(6))
        result["start_date"] = _iso(y1, m1, d1)
        result["end_date"] = _iso(y2, m2, d2)
        result["schedule_pending"] = False
        if has_schedule_flexibility:
            result["schedule_note"] = text.strip().rstrip(".。")
    elif has_schedule_flexibility:
        result["schedule_note"] = text.strip().rstrip(".。")

    movie_title_patterns = [
        r"^\s*영화\s+([^,，]+?)(?:\s*[,，]|$)",
        r"^\s*([^,，]+?)\s+영화\s*(?:[,，]|$)",
    ]
    for pattern in movie_title_patterns:
        movie_title = re.search(pattern, text, re.IGNORECASE)
        if movie_title:
            value = movie_title.group(1).strip()
            if value:
                result["product_name"] = value
                result["product_type"] = "PPV"
                result["product_category"] = "영화"
                break

    if re.fullmatch(r"\s*영화\s*", text):
        result["product_category"] = "영화"
        result["product_type"] = "PPV"

    product_patterns = [
        r"([^\n,，]{1,40}?)\s*(?:프로모션|이벤트)",
        r"([가-힣A-Za-z0-9][가-힣A-Za-z0-9 _-]{0,30}?)\s*(?:프로모션|이벤트)",
        r"(?:상품명?|콘텐츠명?)\s*(?:은|는|:)?\s*([가-힣A-Za-z0-9 _-]+)",
    ]
    if not result.get("product_name"):
        for pattern in product_patterns:
            product = re.search(pattern, text)
            if product:
                value = product.group(1).strip()
                value = re.sub(r"^(?:이번|신규)\s+", "", value)
                if value in {"다른", "새", "새로운", "신규"}:
                    continue
                result["product_name"] = value
                break
    if result.get("benefit"):
        result["benefit_pending"] = False
    return {
        key: value
        for key, value in result.items()
        if value != "" and value is not None
        and not (isinstance(value, (int, float)) and not isinstance(value, bool) and value == 0)
    }

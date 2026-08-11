from __future__ import annotations

import re
from datetime import date
from typing import Any


KNOWN_PPM_PRODUCTS = [
    "CJ ENM",
    "JTBC",
    "TV조선",
    "채널A",
    "지상파 3사",
    "B tv+",
]


def extract_reference_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s<>]+", text)


def normalize_product_name(value: str) -> str:
    """Remove conversational PPV intent prefixes from a stored product name."""
    cleaned = value.strip()
    clauses = [
        clause.strip()
        for clause in re.split(r"[.!?。]+", cleaned)
        if clause.strip()
    ]
    if (
        len(clauses) >= 2
        and re.search(
            r"(?<![A-Za-z])PPV(?![A-Za-z]).*(?:프로모션|이벤트)",
            clauses[0],
            re.IGNORECASE,
        )
    ):
        cleaned = clauses[-1]
        cleaned = re.sub(
            r"^(?:작품|콘텐츠|영화)(?:명)?(?:은|는|이|가|:)?\s*",
            "",
            cleaned,
        ).strip()
    if cleaned.upper().replace(" ", "") in {"MASS", "TARGET", "PPV", "PPM"}:
        return ""
    return cleaned


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


def extract_reward_scheme(text: str) -> dict[str, Any]:
    """Normalize common marketing rewards while preserving the user's wording."""
    raw_text = text.strip().rstrip(".。")
    raw_text = re.sub(
        r"\s*(?:>>|→)?\s*(?:이게|이것이|이 내용이)?\s*"
        r"(?:혜택|리워드)(?:이야|야|이에요|예요|입니다)?\s*$",
        "",
        raw_text,
    ).strip()
    compact = re.sub(r"\s+", "", text).lower()
    if compact in {
        "혜택있어", "혜택있어요", "혜택있음", "혜택있다",
        "리워드있어", "리워드있어요", "리워드있음", "리워드있다",
    }:
        return {}

    has_reward_signal = re.search(
        r"쿠폰|할인|포인트|B\s*캐시|캐시\s*백|포인트\s*백|"
        r"추첨|경품|증정|지급|적립|무료",
        raw_text,
        re.IGNORECASE,
    )
    if not raw_text or not has_reward_signal:
        return {}

    if "추첨" in raw_text:
        reward_type = "RAFFLE"
    elif "쿠폰" in raw_text:
        reward_type = "COUPON"
    elif re.search(r"포인트|B\s*캐시|캐시\s*백|포인트\s*백", raw_text, re.IGNORECASE):
        reward_type = "POINTBACK"
    elif "할인" in raw_text or "무료" in raw_text:
        reward_type = "DISCOUNT"
    else:
        reward_type = "GIFT"

    if re.search(r"신규\s*가입|가입", raw_text):
        trigger = "SUBSCRIPTION"
    elif "구매" in raw_text:
        trigger = "PURCHASE"
    elif re.search(r"참여|응모", raw_text):
        trigger = "PARTICIPATION"
    elif "시청" in raw_text:
        trigger = "WATCH"
    else:
        trigger = "UNSPECIFIED"

    coupon_before_purchase = re.search(
        r"쿠폰.{0,12}(?:받고|발급받아|적용(?:하고|해)).{0,12}구매",
        raw_text,
    )
    if coupon_before_purchase:
        timing = "BEFORE_PURCHASE"
    elif reward_type == "DISCOUNT" and re.search(r"구매\s*시|가입|첫\s*달", raw_text):
        timing = "INSTANT"
    elif re.search(r"구매.{0,8}(?:하면|후|고객|시)", raw_text):
        timing = "AFTER_PURCHASE"
    else:
        timing = "UNSPECIFIED"

    if reward_type == "RAFFLE" or "추첨" in raw_text:
        distribution = "RAFFLE"
    elif "선착순" in raw_text:
        distribution = "FIRST_COME"
    elif "전원" in raw_text or trigger != "UNSPECIFIED":
        distribution = "ALL"
    else:
        distribution = "UNSPECIFIED"

    value_match = re.search(
        r"(\d[\d,.]*)(?:\s*)(%|원|P|포인트|B\s*캐시|캐시)",
        raw_text,
        re.IGNORECASE,
    )
    quantity_match = re.search(r"(\d[\d,]*)\s*(명|대|개)", raw_text)
    reward_name = ""
    if reward_type == "COUPON":
        name_match = re.search(
            r"((?:VOD|B\s*tv|영화|콘텐츠)?\s*(?:할인\s*)?쿠폰)",
            raw_text,
            re.IGNORECASE,
        )
        reward_name = name_match.group(1).strip() if name_match else "할인 쿠폰"
    elif reward_type == "POINTBACK":
        name_match = re.search(r"B\s*캐시|캐시\s*백|포인트\s*백|포인트", raw_text, re.IGNORECASE)
        reward_name = name_match.group(0).strip() if name_match else "포인트백"
    elif reward_type == "RAFFLE":
        name_match = re.search(
            r"추첨(?:을)?\s*(?:통해|해서|하여)?\s*([^,，]{1,30}?)\s*"
            r"(?:\d[\d,]*\s*(?:명|대|개))?\s*(?:증정|지급|제공)",
            raw_text,
        )
        reward_name = name_match.group(1).strip() if name_match else "경품"
    elif reward_type == "GIFT":
        name_match = re.search(
            r"([^,，]{1,30}?)\s*(?:\d[\d,]*\s*(?:명|대|개))?\s*"
            r"(?:증정|지급|제공)",
            raw_text,
        )
        reward_name = name_match.group(1).strip() if name_match else "증정 혜택"

    value = value_match.group(1) if value_match else ""
    unit = value_match.group(2).replace(" ", "") if value_match else ""
    quantity = quantity_match.group(1) if quantity_match else ""
    quantity_unit = quantity_match.group(2) if quantity_match else ""
    audience = ""
    if re.search(r"타겟\s*고객\s*대상|대상\s*고객", raw_text):
        audience = "타겟 고객"
    elif re.search(r"신규\s*(?:가입\s*)?고객", raw_text):
        audience = "신규 고객"
    elif re.search(r"구매\s*고객", raw_text):
        audience = "구매 고객"

    channel_match = re.search(r"팝업|배너|문자|SMS|푸시|알림톡", raw_text, re.IGNORECASE)
    channel = channel_match.group(0).upper() if channel_match else ""
    if channel == "SMS":
        channel = "문자"

    if reward_type == "COUPON":
        normalized_text = f"{value}{unit} " if value else ""
        normalized_text += f"{reward_name} 증정"
    elif reward_type == "POINTBACK":
        if unit == "%":
            normalized_text = f"{value}% {reward_name} 지급"
        elif value:
            normalized_text = f"{reward_name} {value}{unit} 지급"
        else:
            normalized_text = f"{reward_name} 지급"
    elif reward_type == "RAFFLE":
        prize = reward_name or "경품"
        count = f" {quantity}{quantity_unit}" if quantity else ""
        normalized_text = f"추첨으로 {prize}{count} 증정"
    elif reward_type == "GIFT":
        normalized_text = f"{reward_name or '혜택'} 증정"
    else:
        normalized_text = re.sub(
            r"\s*(?:하려고|할게|할거야|진행하려고)\s*$", "", raw_text
        ).strip()

    return {
        "raw_text": raw_text,
        "normalized_text": normalized_text,
        "reward_type": reward_type,
        "trigger": trigger,
        "timing": timing,
        "distribution": distribution,
        "value": value,
        "unit": unit,
        "reward_name": reward_name,
        "quantity": quantity,
        "quantity_unit": quantity_unit,
        "audience": audience,
        "channel": channel,
    }


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
    reward_scheme = extract_reward_scheme(text)
    if reward_scheme:
        result["benefit"] = reward_scheme["normalized_text"]
        result["reward_scheme"] = reward_scheme
        result["benefit_pending"] = False
        if reward_scheme.get("audience"):
            result["target_condition"] = reward_scheme["audience"]
        if reward_scheme.get("channel"):
            result["exposure_method"] = reward_scheme["channel"]
    explicit_benefit = re.match(
        r"^\s*(.+?)\s*(?:>>|→)?\s*(?:이게|이것이|이 내용이)?\s*"
        r"(?:혜택|리워드)(?:이야|야|이에요|예요|입니다)?\s*$",
        text,
    )
    if explicit_benefit:
        benefit_value = explicit_benefit.group(1).strip().rstrip(".。")
        if benefit_value:
            explicit_scheme = extract_reward_scheme(benefit_value)
            result["benefit"] = (
                explicit_scheme["normalized_text"] if explicit_scheme else benefit_value
            )
            if explicit_scheme:
                result["reward_scheme"] = explicit_scheme
            result["benefit_pending"] = False
    is_raffle_benefit = (
        "추첨" in text
        and re.search(r"(?:증정|경품|지급|제공)", text)
    )
    if is_raffle_benefit and not result.get("benefit"):
        result["benefit"] = text.strip().rstrip(".。")
        result["benefit_pending"] = False
    purchase_match = re.search(r"(?:구매|참여|응모)", text)
    is_point_benefit = (
        purchase_match
        and re.search(
            r"\d[\d,]*(?:\.\d+)?\s*(?:%|원|P|포인트|B\s*캐시|캐시)",
            text,
            re.IGNORECASE,
        )
        and re.search(
            r"(?:B\s*캐시|캐시|포인트|증정|지급|적립|캐시\s*백|백)",
            text,
            re.IGNORECASE,
        )
    )
    if is_point_benefit and not is_raffle_benefit and not result.get("benefit"):
        benefit_value = text[purchase_match.start():].strip().rstrip(".。")
        benefit_value = re.sub(
            r"\s*(?:>>|→)?\s*(?:이게|이것이|이 내용이)?\s*"
            r"(?:혜택|리워드)(?:이야|야|이에요|예요|입니다)?\s*$",
            "",
            benefit_value,
        ).strip()
        result["benefit"] = benefit_value
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

    compact_text = re.sub(r"\s+", "", text).lower()
    known_ppm_product = next(
        (
            product
            for product in KNOWN_PPM_PRODUCTS
            if re.sub(r"\s+", "", product).lower() in compact_text
        ),
        "",
    )
    targeted_movie = re.search(
        r"^\s*(.+?)\s+영화\s+미시청\s+고객\s+타겟(?:으로)?\s+"
        r"영화\s+구매\s+(?:프로모션|이벤트)",
        text,
    )
    if targeted_movie:
        title = targeted_movie.group(1).strip()
        result["product_name"] = title
        result["product_type"] = "PPV"
        result["product_category"] = "영화"
        result["audience_type"] = "TARGET"
        result["target_condition"] = f"{title} 영화 미시청 고객"

    is_ppm = (
        re.search(r"(?<![A-Za-z])PPM(?![A-Za-z])", text, re.IGNORECASE)
        or "월정액" in text
        or known_ppm_product
    )
    is_ppv = re.search(r"(?<![A-Za-z])PPV(?![A-Za-z])", text, re.IGNORECASE)
    is_seasonal = re.search(
        r"(?:시즈널|시즌(?:성|별)?|계절)\s*(?:프로모션|이벤트)?",
        text,
        re.IGNORECASE,
    )
    if is_ppm:
        result["product_type"] = "PPM"
        result["product_category"] = "월정액"
        if known_ppm_product:
            result["product_name"] = known_ppm_product
        else:
            ppm_name_match = re.search(
                r"(?<![A-Za-z])PPM(?![A-Za-z])\s+(.+)$",
                text,
                re.IGNORECASE,
            )
            if ppm_name_match:
                ppm_product_name = re.sub(
                    r"(?:이야|야|이에요|예요|입니다|이라고|라고)$",
                    "",
                    ppm_name_match.group(1).strip(),
                ).strip()
                normalized_ppm_name = ppm_product_name.upper().replace(" ", "")
                if normalized_ppm_name not in {
                    "", "MASS", "TARGET", "월정액", "상품", "프로모션", "이벤트",
                }:
                    result["product_name"] = ppm_product_name
    elif is_ppv:
        result["product_type"] = "PPV"
        if "영화" in text:
            result["product_category"] = "영화"
    elif is_seasonal:
        result["product_type"] = "SEASONAL"
        result["product_category"] = "시즈널"
        seasonal_name = re.search(
            r"(?:이벤트명|행사명|시즌\s*테마)\s*(?:은|는|:)?\s*([^,.。\n]+)",
            text,
        )
        if seasonal_name:
            event_name = seasonal_name.group(1).strip()
            result["product_name"] = event_name
            result["event_name"] = event_name

    capa = re.search(r"(?:목표\s*)?(?:capa|모수)\s*(?:는|은|:)?\s*([\d,.]+\s*(?:만|천)?)", text, re.IGNORECASE)
    if capa:
        result["target_capa"] = _number(capa.group(1))
    else:
        bare_capa = re.fullmatch(
            r"\s*([\d,.]+\s*(?:만|천)?)\s*명\s*", text, re.IGNORECASE
        )
        if bare_capa:
            result["target_capa"] = _number(bare_capa.group(1))

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
                benefit_value = re.sub(
                    r"^(?:혜택|리워드)\s*(?:은|는|:)?\s*",
                    "",
                    benefit.group(1),
                ).strip()
                if benefit_value not in {
                    "이야", "야", "이에요", "예요", "입니다", "이라고", "라고",
                    "있어", "있어요", "있음", "있다", "있습니다",
                }:
                    result["benefit"] = benefit_value
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
    partial_slash_start = re.search(
        r"(?<!\d)(?:(\d{4})[./-])?(\d{1,2})[./-](\d{1,2})"
        r"\s*(?:부터|~|-)\s*$",
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
    elif partial_slash_start:
        year = int(partial_slash_start.group(1) or today.year)
        month = int(partial_slash_start.group(2))
        day = int(partial_slash_start.group(3))
        result["start_date"] = _iso(year, month, day)
        result["schedule_pending"] = False
    elif has_schedule_flexibility:
        result["schedule_note"] = text.strip().rstrip(".。")

    normalized_product_name = normalize_product_name(text)
    if normalized_product_name != text.strip():
        result["product_name"] = normalized_product_name
        result["product_type"] = "PPV"
        if re.search(r"^\s*영화", text):
            result["product_category"] = "영화"

    movie_title_patterns = [
        r"^\s*영화\s+([^,，]+?)(?:\s*[,，]|$)",
        r"^\s*([^,，]+?)\s+영화\s*(?:[,，]|$)",
    ]
    if not result.get("product_name"):
        for pattern in movie_title_patterns:
            movie_title = re.search(pattern, text, re.IGNORECASE)
            if movie_title:
                value = movie_title.group(1).strip()
                normalized_value = value.upper().replace(" ", "")
                if value and normalized_value not in {"PPV", "프로모션", "이벤트"}:
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
                normalized_value = value.upper().replace(" ", "")
                looks_like_schedule_question = (
                    bool(re.search(r"\d{1,2}\s*월|\d{1,2}[./-]\d{1,2}", value))
                    or any(
                        word in value
                        for word in (
                            "일정", "기간", "타임", "비는", "빈 자리", "가능",
                            "언제", "구좌", "메인", "하고싶",
                        )
                    )
                )
                starts_with_ack = value.lower().startswith(
                    ("응 ", "네 ", "예 ", "좋아 ", "아니 ")
                )
                if (
                    value in {"다른", "새", "새로운", "신규"}
                    or normalized_value in {
                        "MASS", "TARGET", "PPV", "PPM", "SEASONAL",
                        "시즈널", "시즌", "영화PPV", "월정액PPM",
                    }
                    or looks_like_schedule_question
                    or starts_with_ack
                ):
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

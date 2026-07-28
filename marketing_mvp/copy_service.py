from __future__ import annotations

from typing import Any
import re


def _object_particle(text: str) -> str:
    last = text.rstrip()[-1:]
    if last and "가" <= last <= "힣":
        has_final_consonant = (ord(last) - ord("가")) % 28 != 0
        return "을" if has_final_consonant else "를"
    return "을"


def _normalized_subscription_benefit(benefit: str) -> str:
    normalized = re.sub(r"신규\s*가입\s*시?", "신규 가입 시 ", benefit)
    normalized = re.sub(r"첫\s*달", "첫 달", normalized)
    return " ".join(normalized.split())


def copy_name_alternatives(campaign: dict[str, Any]) -> list[str]:
    product = campaign.get("product_name") or "이 상품"
    benefit = campaign.get("benefit") or ""
    if campaign.get("product_type") == "PPM":
        if "첫" in benefit and "50%" in benefit.replace(" ", ""):
            return [
                f"{product} 첫 달 반값",
                f"첫 달은 반값, {product}",
                f"{product} 50%로 시작",
            ]
        return [
            f"{product} 월정액 혜택",
            f"지금 시작하는 {product}",
            f"{product} 가입 프로모션",
        ]
    return [
        f"{product} 구매 혜택",
        f"{product} 스페셜 프로모션",
        f"지금 만나는 {product}",
    ]


def generate_copy(campaign: dict[str, Any]) -> dict[str, str]:
    product = campaign.get("product_name") or "이 상품"
    benefit = campaign.get("benefit") or "특별 혜택"
    work_facts = (campaign.get("work_facts") or "").strip()
    product_type = campaign.get("product_type") or ""
    if product_type == "PPM" and benefit != "혜택 없음":
        normalized_benefit = _normalized_subscription_benefit(benefit)
        copy = f"{product} {normalized_benefit}".strip().rstrip("!！") + "!"
        event_name = copy_name_alternatives(campaign)[0]
        return {"event_name": event_name, "copy": copy}

    if benefit == "혜택 없음" and work_facts:
        verified_hook = re.split(r"[.!?。\\n]", work_facts, maxsplit=1)[0].strip()
        verified_hook = verified_hook[:60].rstrip()
        copy = f"{verified_hook}"
    elif "추첨" in benefit:
        count_match = re.search(r"(\d[\d,]*)\s*(명|대|개)", benefit)
        count_value = count_match.group(1) if count_match else ""
        count_unit = count_match.group(2) if count_match else ""
        prize_patterns = [
            r"(?:추첨\s*(?:을)?\s*)?(?:통해|하여|해서)\s*(.+?)(?=\s*\d[\d,]*\s*(?:명|대|개)|\s*(?:증정|지급|제공))",
            r"(?:구매|참여|응모)(?:하면|시|한\s*고객)?\s*(.+?)(?=\s*경품|\s*\d[\d,]*\s*(?:명|대|개))",
        ]
        prize = ""
        for pattern in prize_patterns:
            prize_match = re.search(pattern, benefit)
            if prize_match:
                prize = prize_match.group(1).strip()
                break
        if not prize:
            point_prize = re.search(
                r"(\d[\d,]*\s*원\s*(?:B\s*)?포인트(?:백)?)",
                benefit,
                re.IGNORECASE,
            )
            if point_prize:
                prize = point_prize.group(1).strip()
        prize = prize or "경품"
        if count_unit == "명":
            copy = (
                f"{product} 구매 고객 중 {count_value}명을 추첨해 "
                f"{prize}{_object_particle(prize)} 드립니다."
            )
        elif count_unit in ("대", "개"):
            copy = (
                f"{product} 구매 고객을 대상으로 추첨을 통해 "
                f"{prize} {count_value}{count_unit}를 드립니다."
            )
        else:
            copy = (
                f"{product} 구매 고객을 대상으로 추첨해 "
                f"{prize} 혜택을 드립니다."
            )
    elif benefit == "혜택 없음":
        copy = f"지금 {product}를 만나보세요."
    else:
        copy = f"지금 {product}와 함께하세요. {benefit}!"
    return {
        "event_name": f"{product} 스페셜 프로모션",
        "copy": copy,
    }

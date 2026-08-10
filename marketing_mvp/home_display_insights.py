from __future__ import annotations

from typing import Any


SOURCE_NAME = "[INSIGHT][HOME_DISPLAY] B tv 핵심 전시 구좌 인사이트"


def recommend_home_display(campaign: dict[str, Any]) -> dict[str, Any]:
    """Apply verified HOME_DISPLAY guidance without inventing campaign facts."""
    audience = campaign.get("audience_type")
    benefit = campaign.get("benefit") or ""
    reward_scheme = campaign.get("reward_scheme") or {}
    reward_type = reward_scheme.get("reward_type")
    reward_timing = reward_scheme.get("timing")
    is_complex_reward = reward_type in {"RAFFLE", "GIFT"} or any(
        keyword in benefit
        for keyword in ("추첨", "경품", "당첨", "복수 혜택", "참여 조건")
    )
    entry = "Today B tv TARGET" if audience == "TARGET" else "Today B tv MASS"

    def conversion_flow(default_action: str) -> str:
        if reward_type == "COUPON" and reward_timing == "BEFORE_PURCHASE":
            return "쿠폰 발급 → 쿠폰 적용 → 구매"
        if reward_type == "COUPON" and reward_timing == "AFTER_PURCHASE":
            return f"{default_action} → 쿠폰 지급"
        if reward_type == "POINTBACK":
            return f"{default_action} → 포인트·캐시 적립"
        if reward_type == "RAFFLE":
            return f"{default_action} → 추첨 응모"
        if reward_type == "GIFT":
            return f"{default_action} → 혜택 지급"
        if reward_type == "DISCOUNT":
            return f"할인 적용 → {default_action}"
        return default_action

    if campaign.get("product_type") == "PPM":
        is_btv_plus = (
            "btv+" in (campaign.get("product_name") or "").lower().replace(" ", "")
        )
        source = "B tv 이벤트 유형 + 4.2 방송 월정액"
        if is_btv_plus:
            source += " + 4.3 B tv+"
        ppm_conversion = conversion_flow("월정액 가입창")
        if is_complex_reward:
            areas = [entry, "띠배너", "풀페이지 배너", "가입하기 빅배너"]
            flow = (
                f"{entry} 또는 띠배너 → 풀페이지 배너 → "
                f"가입하기 빅배너 → {ppm_conversion}"
            )
            reason = (
                "월정액의 할인과 경품 조건을 상세 랜딩에서 먼저 설명하고, "
                "가입하기 빅배너에서 월정액 가입창으로 연결합니다."
            )
            copy_guidance = (
                "진입 배너에는 가입 혜택을 짧게 쓰고, 경품 조건과 지급 방식은 "
                "풀페이지에 분리합니다."
            )
        else:
            areas = [entry, "띠배너", "가입하기 빅배너"]
            flow = f"{entry} 또는 띠배너 → 가입하기 빅배너 → {ppm_conversion}"
            reason = (
                "월정액 신규가입 할인은 조건이 단순하므로 상세 랜딩 단계를 늘리지 않고 "
                "가입하기 빅배너와 월정액 가입창으로 바로 연결합니다."
            )
            copy_guidance = (
                "상품명, 신규가입 조건, 첫 달 할인율을 한 번에 이해할 수 있게 구분해 씁니다."
            )
        return {
            "source": source,
            "areas": areas,
            "flow": flow,
            "reason": reason,
            "copy_guidance": copy_guidance,
            "caution": (
                "과거 관찰 수치는 성과 보장이 아니며, 실제 편성 전 구좌 가용성과 "
                "최신 성과를 확인해야 합니다. 풀페이지 배너는 최초 노출 구좌로 단독 사용하지 않습니다."
            ),
        }

    ppv_conversion = conversion_flow("구매")
    if is_complex_reward:
        areas = [entry, "2단 배너", "풀페이지 배너"]
        flow = f"{entry} 또는 2단 배너 → 풀페이지 배너 → {ppv_conversion}"
        reason = (
            "경품·추첨 이벤트는 참여 조건, 당첨자 발표일, 지급 방식과 "
            "유의사항을 상세 랜딩에서 설명해야 하므로 풀페이지 배너를 함께 검토합니다."
        )
        copy_guidance = (
            "진입 배너에는 핵심 혜택만 짧게 쓰고, 상세 조건과 유의사항은 "
            "풀페이지 배너에 분리합니다."
        )
    else:
        areas = [entry, "2단 배너", "콘텐츠 시놉시스"]
        flow = f"{entry} 또는 2단 배너 → 콘텐츠 시놉시스 → {ppv_conversion}"
        reason = (
            "조건과 혜택이 단순한 프로모션은 별도 상세 랜딩 없이 "
            "시놉시스로 연결하는 흐름을 우선 검토합니다."
        )
        copy_guidance = "진입 배너에는 고객이 한 번에 이해할 하나의 핵심 메시지를 사용합니다."

    return {
        "source": SOURCE_NAME,
        "areas": areas,
        "flow": flow,
        "reason": reason,
        "copy_guidance": copy_guidance,
        "caution": (
            "과거 관찰 수치는 성과 보장이 아니며, 실제 편성 전 구좌 가용성과 "
            "최신 성과를 확인해야 합니다. 풀페이지 배너는 최초 노출 구좌로 단독 사용하지 않습니다."
        ),
    }

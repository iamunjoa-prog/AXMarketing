from __future__ import annotations

from typing import Any


SOURCE_NAME = "[INSIGHT][HOME_DISPLAY] B tv 핵심 전시 구좌 인사이트"


def recommend_home_display(campaign: dict[str, Any]) -> dict[str, Any]:
    """Apply verified HOME_DISPLAY guidance without inventing campaign facts."""
    audience = campaign.get("audience_type")
    benefit = campaign.get("benefit") or ""
    is_complex_reward = any(
        keyword in benefit
        for keyword in ("추첨", "경품", "당첨", "복수 혜택", "참여 조건")
    )
    entry = "Today B tv TARGET" if audience == "TARGET" else "Today B tv MASS"

    if is_complex_reward:
        areas = [entry, "2단 배너", "풀페이지 배너"]
        flow = f"{entry} 또는 2단 배너 → 풀페이지 배너 → 구매 또는 이벤트 참여"
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
        flow = f"{entry} 또는 2단 배너 → 콘텐츠 시놉시스 → 구매 또는 시청"
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

from __future__ import annotations

from typing import Any

from marketing_mvp.integration_contract import ACTION, make_mermaid


def next_question(campaign: dict[str, Any]) -> str:
    if not campaign.get("product_name"):
        if campaign.get("product_category") == "영화":
            return "영화 작품명을 알려주세요."
        return "어떤 상품의 프로모션인가요?"
    if not campaign.get("audience_type"):
        return "진행 방식은 MASS와 TARGET 중 무엇인가요? 아직 미정이면 다른 기획부터 진행할 수 있습니다."
    if (
        not campaign.get("start_date")
        and not campaign.get("schedule_pending")
    ):
        return "일정이 정해졌나요? 미정이면 ‘일정 미정’이라고 말씀해 주세요."
    if not campaign.get("benefit") and not campaign.get("benefit_pending"):
        return "혜택이 정해졌나요? 미정이면 ‘리워드 미정’이라고 말씀해 주세요."
    if campaign.get("audience_type") == "TARGET" and not campaign.get("target_capa"):
        return "목표 Capa는 몇 명인가요?"
    if not campaign.get("event_name") or not campaign.get("copy"):
        return "다음으로 이벤트명과 카피를 생성할까요?"
    if not campaign.get("exposure_areas"):
        return "다음으로 홈 전시 구좌와 배너 영역을 추천해드릴까요?"
    return "기본 기획 정보가 준비되었습니다. 오른쪽 상태판을 검토한 뒤 기본정보를 확정해 주세요."


def is_affirmative_response(text: str) -> bool:
    normalized = text.strip().lower().replace(" ", "")
    exact_match = normalized in {
        "응", "웅", "네", "넵", "예", "ㅇㅇ", "좋아", "좋아요",
        "그래", "그러자", "해줘", "진행해줘", "시작하자",
    }
    contextual_match = (
        normalized.startswith(("응", "웅", "네", "넵", "예", "좋아", "그래"))
        and any(word in normalized for word in ("다음", "진행", "해줘", "시작"))
    )
    return exact_match or contextual_match


def is_contextual_no_benefit_response(text: str, previous_assistant: str) -> bool:
    if "혜택" not in previous_assistant and "리워드" not in previous_assistant:
        return False
    normalized = text.strip().lower().replace(" ", "")
    return normalized.startswith(("없어", "없음", "없다", "없어요", "없습니다"))


def is_benefit_recommendation_request(text: str) -> bool:
    lowered = text.lower().replace(" ", "")
    has_benefit_word = any(
        word in lowered
        for word in ("혜택", "리워드", "보상", "경품", "포인트백")
    )
    has_request_word = any(
        word in lowered
        for word in (
            "추천", "뭐가좋", "어떤게좋", "정해줘", "제안",
            "검색", "인사이트", "비교", "결정",
        )
    )
    return has_benefit_word and has_request_word


def benefit_recommendation(campaign: dict[str, Any]) -> str:
    product = campaign.get("product_name") or "해당 상품"
    return (
        f"{product} 프로모션의 경품과 포인트백을 비교해볼게요.\n\n"
        "현재 테스트 버전에는 성과 인사이트 검색 API가 연결되지 않아 "
        "실제 과거 성과 수치를 조회한 결과는 아닙니다.\n\n"
        "1. 포인트백 — 혜택을 바로 이해하기 쉽고 폭넓은 구매 참여를 유도하기 좋음\n"
        "2. 추첨 경품 — 한정된 예산으로 경품의 주목도를 활용하기 좋음\n"
        "3. 혼합형 — 소액 포인트백과 추첨 경품을 함께 구성해 참여성과 화제성을 보완\n\n"
        "예상 구매자 수, 전체 리워드 예산, 검토 중인 경품 가격을 알려주시면 "
        "두 안의 비용 구조를 비교할 수 있습니다. 결정 전까지는 ‘리워드 미정’으로 저장할 수 있어요."
    )


def is_copy_generation_request(text: str) -> bool:
    lowered = text.lower().replace(" ", "")
    has_copy_word = any(word in lowered for word in ("카피", "문구"))
    has_action_word = any(
        word in lowered
        for word in ("만들", "생성", "써줘", "작성", "추천", "제안", "정하")
    )
    return has_copy_word and has_action_word


def to_admin_payload(campaign: dict[str, Any]) -> dict[str, Any]:
    return {
        "action": ACTION,
        "mermaidCode": make_mermaid(campaign["assets"]),
        "rawGasData": {
            "assignee": campaign.get("assignee", ""),
            "meta": {
                "campaignName": campaign["event_name"],
                "product": campaign["product_name"],
                "target": campaign["audience_type"],
                "targetSize": int(campaign.get("target_capa") or 0)
                if campaign["audience_type"] == "TARGET" else 0,
                "targetCondition": campaign.get("target_condition", ""),
                "startDate": campaign["start_date"],
                "dueDate": campaign["end_date"],
                "hasCoupon": campaign.get("has_coupon", "N"),
                "couponBenefit": campaign.get("coupon_benefit", "")
                if campaign.get("has_coupon") == "Y" else "",
            },
            "assets": campaign["assets"],
        },
    }

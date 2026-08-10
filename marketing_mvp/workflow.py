from __future__ import annotations

import re
from typing import Any

from marketing_mvp.integration_contract import ACTION, make_mermaid


def next_question(campaign: dict[str, Any]) -> str:
    if not campaign.get("product_name"):
        if campaign.get("product_category") == "영화":
            return "영화 작품명을 알려주세요."
        return "어떤 상품의 프로모션인가요?"
    if not campaign.get("product_type"):
        return "상품 유형은 단건 콘텐츠 PPV와 월정액 PPM 중 무엇인가요?"
    if not campaign.get("audience_type"):
        return "진행 방식은 MASS와 TARGET 중 무엇인가요? 아직 미정이면 다른 기획부터 진행할 수 있습니다."
    if not campaign.get("schedule_pending"):
        if campaign.get("start_date") and not campaign.get("end_date"):
            return "종료일은 언제인가요?"
        if not campaign.get("start_date") or not campaign.get("end_date"):
            return "진행 기간이 정해졌나요? 아직 미정이라면 기간을 추천받아 보실래요?"
    if not campaign.get("benefit") and not campaign.get("benefit_pending"):
        return (
            "어떤 혜택인가요? 할인, 쿠폰, 포인트백, 추첨 경품 중 "
            "편하게 말씀해 주세요. 미정이면 ‘리워드 미정’이라고 말씀해 주세요."
        )
    if campaign.get("audience_type") == "TARGET" and not campaign.get("target_capa"):
        return "목표 Capa는 몇 명인가요?"
    if not campaign.get("exposure_areas"):
        return "다음으로 전시 영역과 추천 배너를 제안해드릴까요?"
    if not campaign.get("event_name") or not campaign.get("copy"):
        return "확정된 전시 영역에 맞춰 배너별 카피를 생성할까요?"
    return "기본 기획 정보가 준비되었습니다. 왼쪽 상태판을 검토해 주세요."


def is_affirmative_response(text: str) -> bool:
    normalized = text.strip().lower().replace(" ", "")
    exact_match = normalized in {
        "응", "웅", "네", "넵", "예", "ㅇㅇ", "좋아", "좋아요",
        "그래", "그러자", "해줘", "진행해줘", "시작하자",
    }
    contextual_match = (
        normalized.startswith(("응", "웅", "네", "넵", "예", "좋아", "그래"))
        and any(
            word in normalized
            for word in ("좋아", "다음", "진행", "해줘", "시작", "확정", "적용")
        )
    )
    recommendation_confirmation = (
        any(
            phrase in normalized
            for phrase in ("추천해준", "추천한", "제안해준", "제안한", "아까추천")
        )
        and any(
            action in normalized
            for action in ("진행", "확정", "적용", "해줘", "할게")
        )
    )
    return exact_match or contextual_match or recommendation_confirmation


def is_campaign_reset_request(text: str) -> bool:
    normalized = text.strip().lower().replace(" ", "")
    cancel_phrases = (
        "지금까지한거취소",
        "지금까지한것취소",
        "현재기획취소",
        "기획취소",
        "전부취소",
        "처음부터다시",
        "새로시작",
    )
    if any(phrase in normalized for phrase in cancel_phrases):
        return True
    starts_another = any(
        phrase in normalized
        for phrase in (
            "다른프로모션",
            "새프로모션",
            "새로운프로모션",
            "다른캠페인",
            "새캠페인",
            "새로운캠페인",
        )
    )
    return starts_another and any(
        word in normalized for word in ("기획", "시작", "진행", "할게", "해줘")
    )


def is_benefit_presence_response(text: str) -> bool:
    normalized = text.strip().lower().replace(" ", "")
    return normalized in {
        "혜택있어", "혜택있어요", "혜택있음", "혜택있다",
        "리워드있어", "리워드있어요", "리워드있음", "리워드있다",
    }


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


def is_period_recommendation_request(
    text: str,
    previous_assistant: str = "",
) -> bool:
    normalized = text.lower().replace(" ", "")
    direct_request = (
        any(word in normalized for word in ("기간", "일정"))
        and any(word in normalized for word in ("추천", "제안", "정해줘"))
    )
    previous_normalized = previous_assistant.lower().replace(" ", "")
    accepted_offer = (
        is_affirmative_response(text)
        and any(
            phrase in previous_normalized
            for phrase in ("기간을추천", "기간추천", "추천받아보실래요")
        )
    )
    return direct_request or accepted_offer


def period_recommendation(campaign: dict[str, Any]) -> str:
    product_type = campaign.get("product_type")
    if product_type == "PPM":
        return (
            "기본안으로는 월 단위 성과를 확인하기 쉬운 4주 운영을 추천해요. "
            "시작하고 싶은 날짜나 월을 알려주시면 실제 기간으로 정리해드릴게요."
        )
    if product_type == "PPV":
        return (
            "기본안으로는 관심이 집중되는 2주 운영을 추천해요. "
            "공개일이나 시작 희망일을 알려주시면 실제 기간으로 정리해드릴게요."
        )
    return "상품 유형을 알려주시면 PPV와 PPM에 맞는 기본 운영 기간을 제안해드릴게요."


def is_copy_revision_request(text: str) -> bool:
    normalized = text.lower().replace(" ", "")
    has_copy_word = any(word in normalized for word in ("카피", "문구", "카피명"))
    has_revision_word = any(
        word in normalized
        for word in (
            "별로", "마음에안", "수정", "다시", "바꿔", "변경", "새로",
            "다른안", "대안",
        )
    )
    return has_copy_word and has_revision_word


def extract_copy_option_choice(text: str, option_count: int = 3) -> int | None:
    match = re.search(r"(?<!\d)([1-9])\s*번?", text)
    if not match:
        return None
    choice = int(match.group(1)) - 1
    return choice if 0 <= choice < option_count else None


def is_copy_generation_request(text: str) -> bool:
    lowered = text.lower().replace(" ", "")
    has_copy_word = any(word in lowered for word in ("카피", "문구"))
    has_action_word = any(
        word in lowered
        for word in ("만들", "생성", "써줘", "작성", "추천", "제안", "정하")
    )
    return has_copy_word and has_action_word


def is_display_plan_request(text: str) -> bool:
    lowered = text.lower().replace(" ", "")
    has_display_word = any(
        word in lowered
        for word in ("전시", "배너", "구좌", "기획안")
    )
    has_action_word = any(
        word in lowered
        for word in ("추천", "제안", "만들", "구성", "정해", "진행")
    )
    return has_display_word and has_action_word


def is_contextual_display_plan_request(
    text: str,
    previous_assistant: str = "",
) -> bool:
    if is_display_plan_request(text):
        return True
    previous_context = previous_assistant.lower().replace(" ", "")
    offered_display_plan = (
        any(word in previous_context for word in ("전시영역", "추천배너", "전시안"))
        and any(word in previous_context for word in ("제안", "추천", "할까요"))
    )
    normalized = text.lower().replace(" ", "")
    accepted_or_requested = is_affirmative_response(text) or any(
        word in normalized
        for word in ("추천해줘", "추천해줄래", "제안해줘", "진행해줘")
    )
    return offered_display_plan and accepted_or_requested


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

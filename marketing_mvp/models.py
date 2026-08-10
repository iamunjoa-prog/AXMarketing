from __future__ import annotations

from typing import Any


def empty_campaign() -> dict[str, Any]:
    return {
        "campaign_id": "",
        "product_name": "",
        "product_type": "",
        "product_category": "",
        "work_facts": "",
        "start_date": "",
        "end_date": "",
        "schedule_pending": False,
        "schedule_note": "",
        "audience_type": "",
        "benefit": "",
        "benefit_pending": False,
        "reward_scheme": {},
        "target_capa": None,
        "available_capa": None,
        "event_name": "",
        "copy": "",
        "reference_urls": [],
        "exposure_areas": [],
        "target_condition": "",
        "has_coupon": "N",
        "coupon_benefit": "",
        "assignee": "",
        "assets": [],
        "mermaid_code": "",
        "userflow_confirmed": False,
        "review_passed": False,
        "status": "DRAFT",
        "capa_checked": False,
    }


def validate_basic_info(campaign: dict[str, Any]) -> list[str]:
    labels = {
        "product_type": "PPV/PPM",
        "product_name": "상품명",
        "start_date": "시작일",
        "end_date": "종료일",
        "audience_type": "MASS/TARGET",
        "benefit": "혜택",
        "event_name": "이벤트명",
        "copy": "이벤트 카피",
    }
    missing = [label for key, label in labels.items() if not campaign.get(key)]
    if campaign.get("audience_type") == "TARGET":
        if not campaign.get("target_capa"):
            missing.append("목표 Capa")
        if not campaign.get("capa_checked"):
            missing.append("Capa 조회")
    if campaign.get("has_coupon") == "Y" and not campaign.get("coupon_benefit"):
        missing.append("쿠폰 혜택")
    return missing


def validate_planning_info(campaign: dict[str, Any]) -> list[str]:
    labels = {
        "product_type": "PPV/PPM",
        "product_name": "상품명",
        "audience_type": "MASS/TARGET",
    }
    missing = [label for key, label in labels.items() if not campaign.get(key)]
    if not campaign.get("benefit") and not campaign.get("benefit_pending"):
        missing.append("혜택")
    if not campaign.get("schedule_pending"):
        if not campaign.get("start_date"):
            missing.append("시작일")
        if not campaign.get("end_date"):
            missing.append("종료일")
    if campaign.get("audience_type") == "TARGET" and not campaign.get("target_capa"):
        missing.append("목표 Capa")
    if campaign.get("has_coupon") == "Y" and not campaign.get("coupon_benefit"):
        missing.append("쿠폰 혜택")
    return missing


def validate_for_confirmation(campaign: dict[str, Any]) -> list[str]:
    missing = validate_basic_info(campaign)
    if not campaign.get("userflow_confirmed"):
        missing.append("Userflow 확정")
    if not campaign.get("assets"):
        missing.append("배너 에셋")
    if not campaign.get("review_passed"):
        missing.append("에셋·카피 검수")
    return missing

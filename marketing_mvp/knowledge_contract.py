from __future__ import annotations

from typing import Any

from marketing_mvp.integration_contract import empty_asset


SLOT_CONTRACTS: list[dict[str, Any]] = [
    {
        "knowledge_name": "Today B tv MASS / TARGET",
        "json_type": "TODAY_BTV",
        "settings": "MASS/TARGET은 캠페인 meta.target으로 구분",
        "owner": "HOME_DISPLAY",
        "status": "확정",
    },
    {
        "knowledge_name": "2단 배너",
        "json_type": "GENERAL_BANNER",
        "settings": 'data.colType = "2단"',
        "owner": "HOME_DISPLAY",
        "status": "확정",
    },
    {
        "knowledge_name": "풀페이지 배너 / 풀페이지 상세 랜딩",
        "json_type": "FULL_PROMO_BANNER",
        "settings": "최초 노출 구좌로 단독 사용하지 않음",
        "owner": "HOME_DISPLAY",
        "status": "확정",
    },
    {
        "knowledge_name": "프로모션 팝업",
        "json_type": "PROMO_POPUP",
        "settings": "풀페이지 상세 랜딩과 별도 배너",
        "owner": "시스템 연동 계약",
        "status": "확정",
    },
    {
        "knowledge_name": "롱배너",
        "json_type": "LONG_BANNER",
        "settings": "콘텐츠 홍보 중심",
        "owner": "HOME_DISPLAY + 영화 PPV",
        "status": "확정",
    },
    {
        "knowledge_name": "시놉시스 배너",
        "json_type": "SYNOPSIS_BANNER",
        "settings": 'data.gnb = ["콘텐츠"]',
        "owner": "영화 PPV + 시스템 연동 계약",
        "status": "확정",
    },
    {
        "knowledge_name": "오핫콘",
        "json_type": "생성 금지",
        "settings": "assets 제외. Mermaid 일반 노드 예외 허용 여부 확인 전 자동 출력 금지",
        "owner": "HOME_DISPLAY + 영화 PPV",
        "status": "확인 필요",
    },
]


OPEN_ISSUES: list[dict[str, str]] = [
    {
        "id": "KC-001",
        "topic": "오핫콘 Mermaid 예외",
        "issue": (
            "지식문서는 일반 진입 노드 표시를 허용하지만 시스템 계약은 "
            "Mermaid UI 노드와 assets의 1:1 일치를 요구합니다."
        ),
        "temporary_rule": "계약 담당자 확인 전 오핫콘 노드와 에셋을 모두 자동 생성하지 않습니다.",
        "status": "확인 필요",
    }
]


def resolve_slot_contract(knowledge_name: str) -> dict[str, Any] | None:
    normalized = knowledge_name.replace(" ", "").lower()
    for item in SLOT_CONTRACTS:
        aliases = item["knowledge_name"].replace(" ", "").lower().split("/")
        if any(alias and alias in normalized for alias in aliases):
            return dict(item)
    return None


def unresolved_issues() -> list[dict[str, str]]:
    return [dict(issue) for issue in OPEN_ISSUES if issue["status"] != "확정"]


def recommendation_to_assets(
    areas: list[str],
    campaign: dict[str, Any],
) -> list[dict[str, Any]]:
    """Convert knowledge-layer slot names into contract-safe asset drafts."""
    type_by_keyword = (
        ("Today B tv", "TODAY_BTV"),
        ("2단 배너", "GENERAL_BANNER"),
        ("풀페이지", "FULL_PROMO_BANNER"),
        ("시놉시스", "SYNOPSIS_BANNER"),
        ("롱배너", "LONG_BANNER"),
        ("프로모션 팝업", "PROMO_POPUP"),
    )
    selected_types: list[str] = []
    for area in areas:
        if "오핫콘" in area:
            continue
        banner_type = next(
            (
                candidate
                for keyword, candidate in type_by_keyword
                if keyword in area
            ),
            None,
        )
        if banner_type and banner_type not in selected_types:
            selected_types.append(banner_type)

    event_name = campaign.get("event_name") or campaign.get("product_name") or ""
    copy = campaign.get("copy") or ""
    assets: list[dict[str, Any]] = []
    for banner_type in selected_types:
        asset = empty_asset(banner_type)
        data = asset["data"]
        if banner_type == "TODAY_BTV":
            data["mainTitle"] = event_name
            data["subText"] = copy
        elif banner_type == "GENERAL_BANNER":
            data["colType"] = "2단"
            data["previewTitle"] = event_name
            data["previewSub"] = copy
            data["bannerCopy"] = copy
        elif banner_type == "FULL_PROMO_BANNER":
            data["mainCopy"] = event_name
            data["subCopy"] = copy
        elif banner_type == "SYNOPSIS_BANNER":
            data["mainTitle"] = event_name
            data["subTitle"] = copy
        elif banner_type == "LONG_BANNER":
            data["copy"] = copy
            data["subTitle"] = event_name
        assets.append(asset)
    return assets

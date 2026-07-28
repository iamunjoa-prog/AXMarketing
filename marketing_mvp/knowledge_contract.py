from __future__ import annotations

from typing import Any

from marketing_mvp.integration_contract import empty_asset, fit_banner_text


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
        "knowledge_name": "가입하기 빅배너",
        "json_type": "BIG_BANNER",
        "settings": 'data.subType = "가입하기형"',
        "owner": "B tv 이벤트 유형 + 방송 월정액 PPM",
        "status": "확정",
    },
    {
        "knowledge_name": "띠배너",
        "json_type": "STRIP_BANNER",
        "settings": "월정액 가입 혜택의 진입 구좌",
        "owner": "B tv 이벤트 유형 + 방송 월정액 PPM",
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


def _ppm_recommendation_to_assets(
    areas: list[str],
    campaign: dict[str, Any],
) -> list[dict[str, Any]]:
    type_by_keyword = (
        ("Today B tv", "TODAY_BTV"),
        ("띠배너", "STRIP_BANNER"),
        ("가입하기 빅배너", "BIG_BANNER"),
        ("풀페이지", "FULL_PROMO_BANNER"),
        ("2단 배너", "GENERAL_BANNER"),
    )
    selected_types: dict[str, str] = {}
    for area in areas:
        banner_type = next(
            (
                candidate
                for keyword, candidate in type_by_keyword
                if keyword in area
            ),
            None,
        )
        if banner_type and banner_type not in selected_types:
            selected_types[banner_type] = area

    event_name = campaign.get("event_name") or campaign.get("product_name") or ""
    product_name = campaign.get("product_name") or event_name
    benefit = campaign.get("benefit") or ""
    copy = campaign.get("copy") or benefit
    short_copy = "지금 가입하기" if benefit == "혜택 없음" else benefit
    normalized_benefit = " ".join(
        benefit.replace("신규가입", "신규 가입").replace("첫달", "첫 달").split()
    )
    if "첫 달" in normalized_benefit and "50%" in normalized_benefit:
        short_copy = "신규 가입 첫 달 50%"
    elif benefit != "혜택 없음":
        short_copy = normalized_benefit
    assets: list[dict[str, Any]] = []
    for banner_type, source_area in selected_types.items():
        asset = empty_asset(banner_type)
        data = asset["data"]

        def set_text(key: str, value: str) -> None:
            data[key] = fit_banner_text(banner_type, key, value)

        if "landingValue" in data:
            data["landingValue"] = "UI_PATH: /monthly_subscribe"
        if banner_type == "TODAY_BTV":
            set_text("mainTitle", event_name)
            set_text("subText", short_copy)
        elif banner_type == "STRIP_BANNER":
            set_text("mainTitle", event_name)
            set_text("subTitle", short_copy)
        elif banner_type == "BIG_BANNER":
            if "가입하기" in source_area:
                data["subType"] = "가입하기형"
            set_text("mainTitle", event_name)
            set_text("subTitle", short_copy)
            set_text("desc", copy)
            set_text("buttonText", "가입하기")
        elif banner_type == "FULL_PROMO_BANNER":
            set_text("mainCopy", event_name)
            set_text("subCopy", copy)
        elif banner_type == "GENERAL_BANNER":
            data["colType"] = "2단"
            set_text("previewTitle", event_name)
            set_text("previewSub", copy)
            set_text("bannerCopy", short_copy)
        assets.append(asset)
    return assets


def recommendation_to_assets(
    areas: list[str],
    campaign: dict[str, Any],
) -> list[dict[str, Any]]:
    """Convert knowledge-layer slot names into contract-safe asset drafts."""
    if campaign.get("product_type") == "PPM":
        return _ppm_recommendation_to_assets(areas, campaign)

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
    product_name = campaign.get("product_name") or event_name
    benefit = campaign.get("benefit") or ""
    if benefit == "혜택 없음":
        short_copy = "지금 만나보세요"
    elif "추첨" in benefit:
        short_copy = "경품 혜택 확인"
    else:
        short_copy = benefit or copy
    assets: list[dict[str, Any]] = []
    for banner_type in selected_types:
        asset = empty_asset(banner_type)
        data = asset["data"]

        def set_text(key: str, value: str) -> None:
            data[key] = fit_banner_text(banner_type, key, value)

        if banner_type == "TODAY_BTV":
            set_text("mainTitle", event_name)
            set_text("subText", copy)
        elif banner_type == "GENERAL_BANNER":
            data["colType"] = "2단"
            set_text("previewTitle", event_name)
            set_text("previewSub", copy)
            set_text("bannerCopy", short_copy)
        elif banner_type == "FULL_PROMO_BANNER":
            set_text("mainCopy", event_name)
            set_text("subCopy", copy)
        elif banner_type == "SYNOPSIS_BANNER":
            set_text("mainTitle", product_name)
            set_text("subTitle", short_copy)
        elif banner_type == "LONG_BANNER":
            set_text("copy", event_name)
            set_text("subTitle", short_copy)
        assets.append(asset)
    return assets

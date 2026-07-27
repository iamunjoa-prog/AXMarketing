from __future__ import annotations

from typing import Any


ACTION = "CREATE_CAMPAIGN_ASSETS"
TEXT_SPEC_SOURCE = (
    "https://docs.google.com/spreadsheets/d/"
    "1Aq9YiYfnSJ9ycHRiEeEXz59FJnTRKVVOzZBMw09hw5A/edit?gid=0#gid=0"
)

BANNER_SPECS: dict[str, dict[str, Any]] = {
    "TODAY_BTV": {
        "label": "Today B tv",
        "url": "https://raw.githubusercontent.com/btvcuration/campaign/main/assets/images/ui-templates/today_btv.png",
        "keys": ["topText", "mainTitle", "subText", "imageUrl", "landingValue", "gnb"],
        "text_limits": {"topText": 9, "mainTitle": 20, "subText": 20},
        "fixed_gnb": ["홈"],
    },
    "MINI_EPG_BANNER": {
        "label": "실시간 EPG 배너",
        "url": "https://raw.githubusercontent.com/btvcuration/campaign/main/assets/images/ui-templates/mini_epg.png",
        "keys": ["imageUrl", "buttonText", "landingValue", "gnb"],
        "text_limits": {"buttonText": 5},
        "fixed_gnb": ["실시간 채널"],
    },
    "GENERAL_BANNER": {
        "label": "일반 배너",
        "url": "https://raw.githubusercontent.com/btvcuration/campaign/main/assets/images/ui-templates/general_banner_2col.png",
        "keys": [
            "colType", "previewTitle", "previewSub", "previewImg",
            "bannerCopy", "bannerImg", "landingValue", "gnb",
        ],
        "text_limits": {"previewTitle": 20, "previewSub": 20, "bannerCopy": 8},
        "enums": {"colType": ["1단", "2단", "3단"]},
    },
    "FULL_PROMO_BANNER": {
        "label": "풀프로모션",
        "url": "https://raw.githubusercontent.com/btvcuration/campaign/main/assets/images/ui-templates/full_promo.png",
        "keys": [
            "bgImg", "topLogo", "mainCopy", "subCopy",
            "card1Title", "card1Sub", "card1Img", "card1Landing",
            "card2Title", "card2Sub", "card2Img", "card2Landing",
            "card3Title", "card3Sub", "card3Img", "card3Landing",
            "landingValue", "gnb",
        ],
        "text_limits": {
            "topLogo": 20,
            "mainCopy": 40,
            "subCopy": 68,
            "card1Title": 10,
            "card1Sub": 10,
            "card2Title": 10,
            "card2Sub": 10,
            "card3Title": 10,
            "card3Sub": 10,
        },
    },
    "BIG_BANNER": {
        "label": "빅배너",
        "url": "https://raw.githubusercontent.com/btvcuration/campaign/main/assets/images/ui-templates/big_banner.png",
        "keys": [
            "subType", "mainTitle", "subTitle", "desc", "buttonText",
            "imageUrl", "landingValue", "gnb",
        ],
        "text_limits": {"mainTitle": 19, "subTitle": 19},
        "enums": {"subType": ["기본형", "가입하기형"]},
    },
    "LONG_BANNER": {
        "label": "롱배너",
        "url": "https://raw.githubusercontent.com/btvcuration/campaign/main/assets/images/ui-templates/long_banner.png",
        "keys": ["copy", "subTitle", "imageUrl", "landingValue", "gnb"],
        "text_limits": {"copy": 17, "subTitle": 12},
    },
    "STRIP_BANNER": {
        "label": "띠배너",
        "url": "https://raw.githubusercontent.com/btvcuration/campaign/main/assets/images/ui-templates/strip_banner.png",
        "keys": ["mainTitle", "subTitle", "imageUrl", "landingValue", "gnb"],
        "text_limits": {"mainTitle": 25, "subTitle": 25},
    },
    "SYNOPSIS_BANNER": {
        "label": "시놉시스 배너",
        "url": "https://raw.githubusercontent.com/btvcuration/campaign/main/assets/images/ui-templates/synopsis_banner.png",
        "keys": ["mainTitle", "subTitle", "badgeText", "imageUrl", "landingValue", "gnb"],
        "text_limits": {"mainTitle": 8, "subTitle": 8},
        "fixed_gnb": ["콘텐츠"],
    },
    "PROMO_POPUP": {
        "label": "프로모션 팝업",
        "url": "https://raw.githubusercontent.com/btvcuration/campaign/main/assets/images/ui-templates/promo_popup.png",
        "keys": ["imageUrl", "buttonText", "closeText", "landingValue", "gnb"],
        "text_limits": {"buttonText": 9, "closeText": 9},
    },
}

OBSERVED_GNB_VALUES = ["홈", "영화시리즈", "콘텐츠", "실시간 채널"]


def text_limit_for(banner_type: str, key: str) -> int | None:
    spec = BANNER_SPECS.get(banner_type, {})
    return spec.get("text_limits", {}).get(key)


def fit_banner_text(banner_type: str, key: str, value: str) -> str:
    """Fit generated copy to the approved Google Sheets character limit."""
    text = " ".join((value or "").split())
    limit = text_limit_for(banner_type, key)
    if not limit or len(text) <= limit:
        return text
    clipped = text[:limit].rstrip()
    if " " in clipped:
        word_safe = clipped.rsplit(" ", 1)[0].rstrip()
        if len(word_safe) >= max(4, limit // 2):
            return word_safe
    return clipped


def empty_asset(banner_type: str) -> dict[str, Any]:
    spec = BANNER_SPECS[banner_type]
    data = {
        key: list(spec["fixed_gnb"]) if key == "gnb" and spec.get("fixed_gnb") else ([] if key == "gnb" else "")
        for key in spec["keys"]
    }
    for key, values in spec.get("enums", {}).items():
        data[key] = values[0]
    return {"name": f"{spec['label']} 배너", "type": banner_type, "data": data}


def make_mermaid(assets: list[dict[str, Any]]) -> str:
    lines = ["graph TD"]
    node_ids: list[str] = []
    for index, asset in enumerate(assets):
        node_id = f"N{index + 1}"
        spec = BANNER_SPECS[asset["type"]]
        label = (
            f"<img src='{spec['url']}' width='100'><br>{spec['label']}"
        )
        lines.append(f'  {node_id}["{label}"]')
        node_ids.append(node_id)
    for left, right in zip(node_ids, node_ids[1:]):
        lines.append(f"  {left} --> {right}")
    return "\n".join(lines)


def validate_asset(asset: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    banner_type = asset.get("type")
    if banner_type not in BANNER_SPECS:
        return [f"허용되지 않은 배너 type: {banner_type}"]
    spec = BANNER_SPECS[banner_type]
    data = asset.get("data")
    if not isinstance(data, dict):
        return [f"{banner_type}.data는 객체여야 합니다."]
    if list(data.keys()) != spec["keys"]:
        errors.append(f"{banner_type}.data Key 또는 순서가 계약과 일치하지 않습니다.")
    for key in spec["keys"]:
        if key not in data:
            errors.append(f"{banner_type}.data.{key}가 누락되었습니다.")
        elif key == "gnb" and not isinstance(data[key], list):
            errors.append(f"{banner_type}.data.gnb는 배열이어야 합니다.")
        elif key != "gnb" and not isinstance(data[key], str):
            errors.append(f"{banner_type}.data.{key}는 문자열이어야 합니다.")
        else:
            limit = text_limit_for(banner_type, key)
            if limit and len(data[key]) > limit:
                errors.append(
                    f"{banner_type}.data.{key}는 최대 {limit}자입니다. "
                    f"현재 {len(data[key])}자"
                )
    if spec.get("fixed_gnb") and data.get("gnb") != spec["fixed_gnb"]:
        errors.append(f"{banner_type}.data.gnb는 {spec['fixed_gnb']} 고정입니다.")
    for key, values in spec.get("enums", {}).items():
        if data.get(key) not in values:
            errors.append(f"{banner_type}.data.{key} 허용값: {', '.join(values)}")
    return errors


def validate_contract(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if list(payload.keys()) != ["action", "mermaidCode", "rawGasData"]:
        errors.append("JSON 최상위 구조가 계약과 일치하지 않습니다.")
    if payload.get("action") != ACTION:
        errors.append(f"action은 {ACTION}이어야 합니다.")
    if not isinstance(payload.get("mermaidCode"), str):
        errors.append("mermaidCode는 문자열이어야 합니다.")
    raw = payload.get("rawGasData")
    if not isinstance(raw, dict) or list(raw.keys()) != ["assignee", "meta", "assets"]:
        return errors + ["rawGasData 구조가 계약과 일치하지 않습니다."]
    meta = raw["meta"]
    meta_keys = [
        "campaignName", "product", "target", "targetSize", "targetCondition",
        "startDate", "dueDate", "hasCoupon", "couponBenefit",
    ]
    if not isinstance(meta, dict) or list(meta.keys()) != meta_keys:
        errors.append("rawGasData.meta Key 또는 순서가 계약과 일치하지 않습니다.")
    else:
        if meta["target"] not in ("TARGET", "MASS"):
            errors.append("target은 TARGET 또는 MASS여야 합니다.")
        if not isinstance(meta["targetSize"], int) or isinstance(meta["targetSize"], bool):
            errors.append("targetSize는 Integer여야 합니다.")
        if meta["target"] == "MASS" and meta["targetSize"] != 0:
            errors.append("MASS의 targetSize는 0이어야 합니다.")
        if meta["hasCoupon"] not in ("Y", "N"):
            errors.append("hasCoupon은 Y 또는 N이어야 합니다.")
        if meta["hasCoupon"] == "N" and meta["couponBenefit"] != "":
            errors.append("쿠폰이 없으면 couponBenefit은 빈 문자열이어야 합니다.")
    assets = raw["assets"]
    if not isinstance(assets, list):
        return errors + ["assets는 배열이어야 합니다."]
    for asset in assets:
        errors.extend(validate_asset(asset))
    expected_mermaid = make_mermaid(assets)
    if payload.get("mermaidCode") != expected_mermaid:
        errors.append("Mermaid UI 노드와 assets가 1:1로 일치하지 않습니다.")
    return errors


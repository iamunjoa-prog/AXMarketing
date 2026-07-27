from __future__ import annotations

from typing import Any


SOURCE_NAME = "4.1. 마케팅 인사이트 (영화 PPV)"
SOURCE_URL = (
    "https://docs.google.com/document/d/"
    "1kK2rlUXbURraANBCQMIfDrMBHZ5X6us9nmvfe6Tly4s/edit"
)


def assess_movie_copy(campaign: dict[str, Any]) -> dict[str, Any]:
    """Return the verified Movie PPV copy policy applicable to this campaign."""
    if campaign.get("product_category") != "영화":
        return {
            "applies": False,
            "ready": True,
            "source": SOURCE_NAME,
            "mode": "not_applicable",
            "guidance": "",
            "message": "",
        }

    work_facts = (campaign.get("work_facts") or "").strip()
    benefit = (campaign.get("benefit") or "").strip()
    if benefit and benefit != "혜택 없음":
        return {
            "applies": True,
            "ready": True,
            "source": SOURCE_NAME,
            "mode": "benefit_only",
            "guidance": (
                "작품 내용을 추측하지 않고 사용자가 확정한 구매 조건과 혜택만 "
                "명확하게 안내하는 카피로 제한합니다."
            ),
            "message": "",
        }

    if work_facts:
        return {
            "applies": True,
            "ready": True,
            "source": SOURCE_NAME,
            "mode": "verified_work_facts",
            "guidance": (
                "확인된 작품 정보에서 하나의 구체적인 후킹 포인트만 사용하고, "
                "과장 표현과 스포일러를 피합니다."
            ),
            "message": "",
        }

    return {
        "applies": True,
        "ready": False,
        "source": SOURCE_NAME,
        "mode": "needs_work_facts",
        "guidance": "제목만으로 장르, 줄거리, 인물 관계나 관전 포인트를 만들지 않습니다.",
        "message": (
            "매니저님, 작품 고유의 카피를 작성하려면 공식 줄거리, 예고편 URL "
            "또는 참고할 기사 URL 중 하나가 필요합니다. 현재 테스트 버전은 URL "
            "본문을 직접 읽지 못하므로, 공식 작품 정보를 상태판에 붙여 넣어 주세요."
        ),
    }

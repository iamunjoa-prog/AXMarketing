from __future__ import annotations

import unittest

from marketing_mvp.integration_contract import (
    fit_banner_text,
    validate_asset,
)
from marketing_mvp.knowledge_contract import recommendation_to_assets


class BannerTextSpecTests(unittest.TestCase):
    def test_fit_banner_text_respects_sheet_limit(self) -> None:
        fitted = fit_banner_text(
            "GENERAL_BANNER",
            "bannerCopy",
            "아주 긴 배너 카피입니다",
        )
        self.assertLessEqual(len(fitted), 8)

    def test_validate_asset_reports_over_limit_text(self) -> None:
        asset = {
            "name": "2단 배너",
            "type": "GENERAL_BANNER",
            "data": {
                "colType": "2단",
                "previewTitle": "",
                "previewSub": "",
                "previewImg": "",
                "bannerCopy": "123456789",
                "bannerImg": "",
                "landingValue": "",
                "gnb": [],
            },
        }
        errors = validate_asset(asset)
        self.assertTrue(any("최대 8자" in error for error in errors))

    def test_recommended_assets_generate_banner_specific_copy(self) -> None:
        campaign = {
            "product_name": "테스트 영화",
            "event_name": "테스트 영화 스페셜 프로모션",
            "copy": "지금 테스트 영화와 함께하세요. 특별한 혜택을 드립니다.",
            "benefit": "혜택 없음",
        }
        assets = recommendation_to_assets(
            ["Today B tv", "2단 배너", "시놉시스 배너"],
            campaign,
        )
        for asset in assets:
            self.assertEqual(validate_asset(asset), [])


if __name__ == "__main__":
    unittest.main()
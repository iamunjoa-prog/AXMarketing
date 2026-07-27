from __future__ import annotations

import unittest
from datetime import date

from marketing_mvp.copy_service import generate_copy
from marketing_mvp.extractor import extract_fields
from marketing_mvp.home_display_insights import recommend_home_display
from marketing_mvp.integration_contract import validate_asset
from marketing_mvp.knowledge_contract import recommendation_to_assets
from marketing_mvp.ppm_insights import assess_ppm_campaign


class PpmKnowledgeTests(unittest.TestCase):
    def test_monthly_product_and_discount_are_extracted(self) -> None:
        product = extract_fields(
            "CJ ENM 방송 월정액 프로모션 진행할거야",
            today=date(2026, 7, 28),
        )
        benefit = extract_fields(
            "신규가입시 첫달 50% 할인",
            today=date(2026, 7, 28),
        )
        self.assertEqual(product["product_name"], "CJ ENM 방송 월정액")
        self.assertEqual(product["product_type"], "PPM")
        self.assertEqual(product["product_category"], "월정액")
        self.assertEqual(benefit["benefit"], "신규가입시 첫달 50% 할인")

    def test_btv_plus_is_classified_as_ppm(self) -> None:
        extracted = extract_fields("B tv+ 프로모션 진행", today=date(2026, 7, 28))
        self.assertEqual(extracted["product_name"], "B tv+")
        self.assertEqual(extracted["product_type"], "PPM")

    def test_ppm_display_and_copy_follow_monthly_subscription_flow(self) -> None:
        campaign = {
            "product_name": "CJ ENM 방송 월정액",
            "product_type": "PPM",
            "product_category": "월정액",
            "audience_type": "TARGET",
            "benefit": "신규가입시 첫달 50% 할인",
            "start_date": "2026-08-01",
            "end_date": "2026-08-31",
        }
        recommendation = recommend_home_display(campaign)
        self.assertEqual(
            recommendation["areas"],
            ["Today B tv TARGET", "띠배너", "가입하기 빅배너"],
        )
        self.assertIn("월정액 가입창", recommendation["flow"])
        self.assertNotIn("시놉시스", recommendation["flow"])

        campaign.update(generate_copy(campaign))
        self.assertIn("신규 가입 시 첫 달 50% 할인", campaign["copy"])
        assets = recommendation_to_assets(recommendation["areas"], campaign)
        self.assertEqual(
            [asset["type"] for asset in assets],
            ["TODAY_BTV", "STRIP_BANNER", "BIG_BANNER"],
        )
        for asset in assets:
            self.assertEqual(validate_asset(asset), [])
            self.assertEqual(
                asset["data"]["landingValue"],
                "UI_PATH: /monthly_subscribe",
            )
        big_banner = assets[-1]
        self.assertEqual(big_banner["data"]["subType"], "가입하기형")

    def test_ppm_knowledge_router_separates_general_and_btv_plus(self) -> None:
        general = assess_ppm_campaign(
            {
                "product_name": "CJ ENM 방송 월정액",
                "product_type": "PPM",
                "benefit": "신규가입시 첫달 50% 할인",
            }
        )
        self.assertEqual(general["track"], "방송 월정액 PPM")
        self.assertEqual(len(general["sources"]), 2)
        self.assertIn("CJ ENM", general["guidance"])

        btv_plus = assess_ppm_campaign(
            {
                "product_name": "B tv+",
                "product_type": "PPM",
                "benefit": "12개월 50% 할인",
                "target_capa": 230_000,
                "start_date": "2026-08-03",
                "end_date": "2026-08-07",
            }
        )
        self.assertEqual(btv_plus["track"], "B tv+ 특화 PPM")
        self.assertEqual(len(btv_plus["sources"]), 3)
        self.assertIn("PPM 유료 경험군", btv_plus["recommendation"])
        self.assertIn("주말", btv_plus["recommendation"])


if __name__ == "__main__":
    unittest.main()

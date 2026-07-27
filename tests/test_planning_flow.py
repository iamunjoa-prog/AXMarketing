from __future__ import annotations

import unittest

from marketing_mvp.extractor import extract_fields
from marketing_mvp.models import validate_planning_info
from marketing_mvp.workflow import (
    is_affirmative_response,
    is_campaign_reset_request,
    is_display_plan_request,
    next_question,
)


class PlanningFlowTests(unittest.TestCase):
    def test_display_plan_intent_is_detected(self) -> None:
        self.assertTrue(is_display_plan_request("전시 영역과 배너 추천해줘"))
        self.assertTrue(is_display_plan_request("기획안 만들어줘"))
        self.assertFalse(is_display_plan_request("카피 만들어줘"))

    def test_confirmation_language_is_detected(self) -> None:
        self.assertTrue(is_affirmative_response("응 이대로 확정해줘"))
        self.assertTrue(is_affirmative_response("네 적용해줘"))

    def test_ambiguous_product_requests_ppv_or_ppm(self) -> None:
        question = next_question({"product_name": "테스트 상품"})
        self.assertIn("PPV", question)
        self.assertIn("PPM", question)

    def test_new_campaign_and_cancel_intents_are_detected(self) -> None:
        self.assertTrue(is_campaign_reset_request("다른 프로모션 기획할게"))
        self.assertTrue(is_campaign_reset_request("지금까지한거 취소"))
        self.assertFalse(is_campaign_reset_request("쿠폰 발급 취소"))

    def test_new_campaign_intent_is_not_extracted_as_product(self) -> None:
        self.assertNotIn("product_name", extract_fields("다른 프로모션 기획할게"))

    def test_planning_validation_does_not_require_copy(self) -> None:
        campaign = {
            "product_name": "테스트 영화",
            "product_type": "PPV",
            "audience_type": "MASS",
            "benefit": "혜택 없음",
            "start_date": "2026-07-28",
            "end_date": "2026-08-10",
            "schedule_pending": False,
            "event_name": "",
            "copy": "",
            "has_coupon": "N",
        }
        self.assertEqual(validate_planning_info(campaign), [])


if __name__ == "__main__":
    unittest.main()
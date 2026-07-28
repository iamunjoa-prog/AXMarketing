from __future__ import annotations

import unittest

from marketing_mvp.extractor import extract_fields, normalize_product_name
from marketing_mvp.models import validate_planning_info
from marketing_mvp.workflow import (
    extract_copy_option_choice,
    is_affirmative_response,
    is_campaign_reset_request,
    is_copy_revision_request,
    is_display_plan_request,
    is_period_recommendation_request,
    next_question,
    period_recommendation,
)


class PlanningFlowTests(unittest.TestCase):
    def test_display_plan_intent_is_detected(self) -> None:
        self.assertTrue(is_display_plan_request("전시 영역과 배너 추천해줘"))
        self.assertTrue(is_display_plan_request("기획안 만들어줘"))
        self.assertFalse(is_display_plan_request("카피 만들어줘"))

    def test_confirmation_language_is_detected(self) -> None:
        self.assertTrue(is_affirmative_response("응 이대로 확정해줘"))
        self.assertTrue(is_affirmative_response("네 적용해줘"))
        self.assertTrue(is_affirmative_response("응 좋아"))
        self.assertTrue(is_affirmative_response("아까 추천해준 3개 진행"))

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

    def test_mass_intent_is_not_saved_as_product_name(self) -> None:
        extracted = extract_fields("Mass 프로모션 진행하려고")
        self.assertEqual(extracted["audience_type"], "MASS")
        self.assertNotIn("product_name", extracted)

    def test_known_ppm_product_is_understood_without_reasking(self) -> None:
        extracted = extract_fields("PPM CJ ENM이야")
        self.assertEqual(extracted["product_name"], "CJ ENM")
        self.assertEqual(extracted["product_type"], "PPM")
        self.assertEqual(extracted["product_category"], "월정액")
        for product in ("JTBC", "TV조선", "채널A", "지상파 3사", "B tv+"):
            with self.subTest(product=product):
                known = extract_fields(f"{product}이야")
                self.assertEqual(known["product_name"], product)
                self.assertEqual(known["product_type"], "PPM")

    def test_period_recommendation_offer_and_acceptance(self) -> None:
        question = next_question(
            {
                "product_name": "CJ ENM",
                "product_type": "PPM",
                "audience_type": "MASS",
            }
        )
        self.assertIn("기간을 추천", question)
        self.assertTrue(
            is_period_recommendation_request("응", question)
        )
        self.assertIn(
            "4주",
            period_recommendation({"product_type": "PPM"}),
        )

    def test_copy_revision_and_option_choice_are_detected(self) -> None:
        self.assertTrue(is_copy_revision_request("카피가 너무 별로야"))
        self.assertTrue(is_copy_revision_request("카피명 다시 수정해줘"))
        self.assertEqual(extract_copy_option_choice("2번으로 해줘", 3), 1)

    def test_ppv_intent_sentence_is_not_saved_as_movie_title(self) -> None:
        extracted = extract_fields(
            "영화 PPV 프로모션할거야. 악마는 프라다를 입는다 2"
        )
        self.assertEqual(extracted["product_name"], "악마는 프라다를 입는다 2")
        self.assertEqual(extracted["product_type"], "PPV")
        self.assertEqual(extracted["product_category"], "영화")
        self.assertEqual(
            normalize_product_name(
                "PPV 프로모션할거야. 악마는 프라다를 입는다 2"
            ),
            "악마는 프라다를 입는다 2",
        )

    def test_complete_schedule_moves_to_benefit_question(self) -> None:
        question = next_question(
            {
                "product_name": "악마는 프라다를 입는다 2",
                "product_type": "PPV",
                "audience_type": "MASS",
                "start_date": "2026-07-21",
                "end_date": "2026-07-31",
            }
        )
        self.assertIn("혜택", question)

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
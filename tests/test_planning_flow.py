from __future__ import annotations

import unittest

from marketing_mvp.extractor import (
    extract_fields,
    extract_reward_scheme,
    normalize_product_name,
)
from marketing_mvp.home_display_insights import recommend_home_display
from marketing_mvp.models import validate_planning_info
from marketing_mvp.workflow import (
    extract_copy_option_choice,
    is_affirmative_response,
    is_benefit_presence_response,
    is_campaign_reset_request,
    is_copy_revision_request,
    is_contextual_display_plan_request,
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

    def test_display_plan_intent_uses_previous_question_context(self) -> None:
        previous = "다음으로 전시 영역과 추천 배너를 제안해드릴까요?"
        self.assertTrue(is_contextual_display_plan_request("응", previous))
        self.assertTrue(is_contextual_display_plan_request("추천해줄래", previous))
        self.assertFalse(
            is_contextual_display_plan_request("추천해줄래", "혜택이 정해졌나요?")
        )

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

    def test_partial_schedule_saves_start_and_requests_end_date(self) -> None:
        extracted = extract_fields("8/21~", today=__import__("datetime").date(2026, 8, 10))
        self.assertEqual(extracted["start_date"], "2026-08-21")
        self.assertNotIn("end_date", extracted)
        question = next_question({
            "product_name": "악마는 프라다를 입는다 2",
            "product_type": "PPV",
            "audience_type": "MASS",
            "start_date": extracted["start_date"],
        })
        self.assertEqual(question, "종료일은 언제인가요?")

    def test_reward_schemes_are_normalized(self) -> None:
        cases = [
            ("구매하면 포인트백", "POINTBACK", "AFTER_PURCHASE", "ALL", "포인트백 지급"),
            ("구매하면 VOD 할인 쿠폰 증정", "COUPON", "AFTER_PURCHASE", "ALL", "VOD 할인 쿠폰 증정"),
            ("VOD 할인 쿠폰 받고 구매", "COUPON", "BEFORE_PURCHASE", "ALL", "VOD 할인 쿠폰 증정"),
            ("구매하면 추첨 통해 경품 증정", "RAFFLE", "AFTER_PURCHASE", "RAFFLE", "추첨으로 경품 증정"),
            ("구매 시 30% 할인", "DISCOUNT", "INSTANT", "ALL", "구매 시 30% 할인"),
        ]
        for text, reward_type, timing, distribution, normalized in cases:
            with self.subTest(text=text):
                reward = extract_reward_scheme(text)
                self.assertEqual(reward["reward_type"], reward_type)
                self.assertEqual(reward["timing"], timing)
                self.assertEqual(reward["distribution"], distribution)
                self.assertEqual(extract_fields(text)["benefit"], normalized)

    def test_reward_timing_changes_recommended_userflow(self) -> None:
        base_campaign = {
            "product_name": "테스트 영화",
            "product_type": "PPV",
            "audience_type": "MASS",
        }
        before = dict(base_campaign)
        before.update(extract_fields("VOD 할인 쿠폰 받고 구매"))
        self.assertIn(
            "쿠폰 발급 → 쿠폰 적용 → 구매",
            recommend_home_display(before)["flow"],
        )
        after = dict(base_campaign)
        after.update(extract_fields("구매하면 VOD 할인 쿠폰 증정"))
        self.assertIn("구매 → 쿠폰 지급", recommend_home_display(after)["flow"])
        pointback = dict(base_campaign)
        pointback.update(extract_fields("구매하면 포인트백"))
        self.assertIn(
            "구매 → 포인트·캐시 적립",
            recommend_home_display(pointback)["flow"],
        )

    def test_benefit_presence_is_not_saved_as_benefit(self) -> None:
        self.assertTrue(is_benefit_presence_response("혜택 있어"))
        self.assertNotIn("benefit", extract_fields("혜택 있어"))

    def test_b_cashback_is_extracted_as_benefit(self) -> None:
        expected = "구매하면 30% B캐시 백"
        self.assertEqual(extract_fields(expected)["benefit"], "30% B캐시 지급")
        clarified = extract_fields(f"{expected} >> 이게 혜택이야")
        self.assertEqual(clarified["benefit"], "30% B캐시 지급")

        fixed_points = extract_fields("구매하면 B캐시 1000P")
        self.assertEqual(fixed_points["benefit"], "B캐시 1000P 지급")
        self.assertEqual(fixed_points["reward_scheme"]["reward_type"], "POINTBACK")
        self.assertEqual(fixed_points["reward_scheme"]["value"], "1000")
        self.assertEqual(fixed_points["reward_scheme"]["unit"], "P")

    def test_target_campaign_sentence_is_split_into_fields(self) -> None:
        extracted = extract_fields(
            "군체 영화 미시청 고객 타겟으로 영화 구매 프로모션"
        )
        self.assertEqual(extracted["product_name"], "군체")
        self.assertEqual(extracted["product_type"], "PPV")
        self.assertEqual(extracted["audience_type"], "TARGET")
        self.assertEqual(extracted["target_condition"], "군체 영화 미시청 고객")

    def test_contextual_target_capa_and_reward_context_are_normalized(self) -> None:
        self.assertEqual(extract_fields("40만명")["target_capa"], 400_000)
        extracted = extract_fields(
            "타겟 고객 대상 팝업으로 영화 할인 쿠폰 증정하려고"
        )
        self.assertEqual(extracted["benefit"], "영화 할인 쿠폰 증정")
        self.assertEqual(extracted["target_condition"], "타겟 고객")
        self.assertEqual(extracted["exposure_method"], "팝업")
        self.assertIn("증정하려고", extracted["reward_scheme"]["raw_text"])
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

    def test_planning_validation_accepts_pending_benefit(self) -> None:
        campaign = {
            "product_name": "CJ ENM",
            "product_type": "PPM",
            "audience_type": "MASS",
            "benefit": "",
            "benefit_pending": True,
            "start_date": "2026-08-01",
            "end_date": "2026-08-31",
            "schedule_pending": False,
            "has_coupon": "N",
        }
        self.assertEqual(validate_planning_info(campaign), [])


if __name__ == "__main__":
    unittest.main()

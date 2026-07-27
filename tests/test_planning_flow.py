from __future__ import annotations

import unittest

from marketing_mvp.models import validate_planning_info
from marketing_mvp.workflow import (
    is_affirmative_response,
    is_display_plan_request,
)


class PlanningFlowTests(unittest.TestCase):
    def test_display_plan_intent_is_detected(self) -> None:
        self.assertTrue(is_display_plan_request("전시 영역과 배너 추천해줘"))
        self.assertTrue(is_display_plan_request("기획안 만들어줘"))
        self.assertFalse(is_display_plan_request("카피 만들어줘"))

    def test_confirmation_language_is_detected(self) -> None:
        self.assertTrue(is_affirmative_response("응 이대로 확정해줘"))
        self.assertTrue(is_affirmative_response("네 적용해줘"))

    def test_planning_validation_does_not_require_copy(self) -> None:
        campaign = {
            "product_name": "테스트 영화",
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
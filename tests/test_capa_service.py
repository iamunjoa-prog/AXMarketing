from __future__ import annotations

import unittest

from marketing_mvp.capa_service import GoogleSheetCapaService


class StubGoogleSheetCapaService(GoogleSheetCapaService):
    def _rows(self) -> list[dict[str, str]]:
        return [
            {
                "날짜": "2026. 8. 21",
                "배너 잔여 슬롯": "0",
                "쿠폰 잔여 슬롯": "2640000",
            },
            {
                "날짜": "2026. 8. 22",
                "배너 잔여 슬롯": "100000",
                "쿠폰 잔여 슬롯": "2700000",
            },
        ]


class CapaServiceTests(unittest.TestCase):
    def test_both_slots_are_checked_for_each_campaign_date(self) -> None:
        result = StubGoogleSheetCapaService().check(
            "2026-08-21", "2026-08-22", 400_000, "both"
        )
        self.assertEqual(result["minimum_banner_available"], 0)
        self.assertEqual(result["minimum_coupon_available"], 2_640_000)
        self.assertFalse(result["is_possible"])
        self.assertEqual(result["covered_days"], 2)
        self.assertEqual(result["expected_days"], 2)

    def test_coupon_only_campaign_uses_coupon_slot(self) -> None:
        result = StubGoogleSheetCapaService().check(
            "2026-08-21", "2026-08-22", 400_000, "coupon"
        )
        self.assertEqual(result["available_capa"], 2_640_000)
        self.assertTrue(result["is_possible"])


if __name__ == "__main__":
    unittest.main()

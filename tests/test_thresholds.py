from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_threshold_analysis  # noqa: E402


class ThresholdAnalysisTests(unittest.TestCase):
    def test_thresholds_are_directional_and_identify_current_cap(self):
        result = build_threshold_analysis.analyze()
        quantities = result["required_collateral_quantity_for_target"]
        declines = result["max_price_decline_for_target"]
        self.assertLess(Decimal(quantities["2000000"]), Decimal(quantities["3000000"]))
        self.assertLess(Decimal(quantities["3000000"]), Decimal(quantities["4000000"]))
        self.assertGreater(Decimal(declines["2000000"]), Decimal(declines["3000000"]))
        self.assertEqual(result["maximum_non_collateral_limit_name"], "concentration")
        self.assertEqual(result["maximum_non_collateral_limit_usd"], "4000000.00")
        self.assertFalse(result["full_request_feasible_under_current_caps"])

    def test_three_million_break_even_reproduces_required_proceeds(self):
        result = build_threshold_analysis.analyze()
        quantity = Decimal("4000000")
        price_decline = Decimal(result["max_price_decline_for_target"]["3000000"])
        post_cost_factor = Decimal(result["post_cost_factor_before_price_stress"])
        proceeds = quantity * (Decimal("1") - price_decline) * post_cost_factor - Decimal("20000")
        self.assertAlmostEqual(proceeds, Decimal("3750000"), delta=Decimal("3"))

    def test_decision_surface_is_complete_and_monotonic(self):
        result = build_threshold_analysis.analyze()
        surface = result["decision_surface"]
        self.assertEqual(len(surface["cells"]), 40)
        cells = {
            (Decimal(row["collateral_quantity_usdc"]), Decimal(row["price_stress_pct"])): Decimal(row["recommended_amount_usd"])
            for row in surface["cells"]
        }
        for quantity in map(Decimal, surface["quantity_axis_usdc"]):
            limits = [cells[(quantity, Decimal(stress))] for stress in surface["price_stress_axis_pct"]]
            self.assertTrue(all(left >= right for left, right in zip(limits, limits[1:])))
        for stress in map(Decimal, surface["price_stress_axis_pct"]):
            limits = [cells[(Decimal(quantity), stress)] for quantity in surface["quantity_axis_usdc"]]
            self.assertTrue(all(left <= right for left, right in zip(limits, limits[1:])))
        self.assertEqual(cells[(Decimal("4000000.00"), Decimal("0.02"))], Decimal("3000000.00"))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_collateral_call_ladder  # noqa: E402


class CollateralCallLadderTests(unittest.TestCase):
    def test_base_passes_and_first_grid_call_is_five_percent(self):
        result = build_collateral_call_ladder.build()
        self.assertEqual(result["first_grid_call_stress_pct"], "0.05")
        self.assertEqual(result["rows"][0]["status"], "PASS")
        self.assertEqual(result["rows"][1]["status"], "CALL_REQUIRED")
        self.assertEqual(result["rows"][0]["covenant_headroom_usd"], "58100.00")

    def test_cures_rise_and_supported_commitment_falls(self):
        rows = build_collateral_call_ladder.build()["rows"]
        topups = [Decimal(row["top_up_required_usdc"]) for row in rows]
        repayments = [Decimal(row["repayment_required_usd"]) for row in rows]
        commitments = [Decimal(row["rounded_coverage_compliant_commitment_usd"]) for row in rows]
        self.assertTrue(all(a <= b for a, b in zip(topups, topups[1:])))
        self.assertTrue(all(a <= b for a, b in zip(repayments, repayments[1:])))
        self.assertTrue(all(a >= b for a, b in zip(commitments, commitments[1:])))

    def test_exact_trigger_reproduces_required_proceeds(self):
        result = build_collateral_call_ladder.build()
        trigger = Decimal(result["exact_modeled_breach_price_stress_pct"])
        proceeds = Decimal("4000000") * (Decimal("1") - trigger) * Decimal("0.9925") - Decimal("20000")
        self.assertAlmostEqual(proceeds, Decimal(result["required_proceeds_usd"]), delta=Decimal("3"))


if __name__ == "__main__":
    unittest.main()

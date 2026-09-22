import unittest
from decimal import Decimal

from scripts.build_liquidity_analysis import calculate, load_values


class LiquidityAnalysisTests(unittest.TestCase):
    def test_public_data_bridge_reconciles(self):
        result = calculate(load_values())
        self.assertEqual(result["residual_before_potential_put_usd"], "96810000.00")
        self.assertEqual(result["residual_after_potential_put_usd"], "-194790000.00")
        self.assertIn("not a borrowing-entity cash forecast", result["method_limit"])

    def test_larger_potential_put_cannot_improve_residual(self):
        values = load_values()
        base = calculate(values)
        values["FIN-012"] += Decimal("1000000")
        stressed = calculate(values)
        self.assertLessEqual(
            Decimal(stressed["residual_after_potential_put_usd"]),
            Decimal(base["residual_after_potential_put_usd"]),
        )


if __name__ == "__main__":
    unittest.main()

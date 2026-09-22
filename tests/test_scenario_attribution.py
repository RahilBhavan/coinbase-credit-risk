import unittest

from scripts.build_scenario_attribution import build


class ScenarioAttributionTests(unittest.TestCase):
    def test_every_engine_scenario_has_complete_attribution(self):
        payload = build()
        rows = payload["rows"]
        self.assertEqual(payload["summary"], {
            "scenario_count": 11,
            "same_limit_count": 2,
            "reduced_limit_count": 5,
            "decline_count": 4,
            "hard_blocker_scenario_count": 3,
            "maximum_recommendation_loss_usd": "3000000.00",
        })
        self.assertEqual(len({row["scenario_id"] for row in rows}), 11)
        self.assertEqual({row["severity_rank"] for row in rows}, set(range(1, 12)))
        for row in rows:
            self.assertTrue(row["primary_driver"])
            self.assertTrue(row["resolution_evidence"])

    def test_key_scenarios_name_the_actual_constraint(self):
        rows = {row["scenario_id"]: row for row in build()["rows"]}
        self.assertEqual(rows["borrower_cash_stress"]["binding_cap"], "obligor")
        self.assertEqual(rows["borrower_cash_stress"]["primary_driver"], "obligor_capacity")
        self.assertEqual(rows["correlated_portfolio_stress"]["binding_cap"], "concentration")
        self.assertEqual(rows["route_failure"]["binding_cap"], "hard_blocker")
        self.assertEqual(rows["route_failure"]["recommendation_delta_vs_base_usd"], "-3000000.00")

    def test_method_limit_rejects_predictive_interpretation(self):
        limit = build()["method_limit"]
        for token in ("not a probability", "forecast", "causal estimate", "new decision rule"):
            self.assertIn(token, limit)


if __name__ == "__main__":
    unittest.main()

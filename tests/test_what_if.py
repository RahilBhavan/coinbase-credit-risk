import unittest

from scripts.build_what_if_contract import build, evaluate


class WhatIfContractTests(unittest.TestCase):
    def test_declared_vectors_reconcile(self):
        contract = build()
        for vector in contract["test_vectors"]:
            self.assertEqual(evaluate(contract, vector["inputs"]), vector["expected"], vector["vector_id"])

    def test_base_and_hard_blocker_match_decision_contract(self):
        contract = build()
        vectors = {row["vector_id"]: row["expected"] for row in contract["test_vectors"]}
        self.assertEqual(vectors["base"]["available_proceeds_usd"], "3870600.00")
        self.assertEqual(vectors["base"]["recommended_amount_usd"], "3000000.00")
        self.assertEqual(vectors["ownership_blocker"]["recommended_amount_usd"], "0.00")
        self.assertEqual(vectors["ownership_blocker"]["binding_cap"], "hard_blocker")

    def test_bounds_and_method_limit_are_explicit(self):
        contract = build()
        self.assertEqual(set(contract["bounds"]), {"quantity_usdc", "price_stress_pct", "additional_route_delay_hours", "execution_cost_bps"})
        self.assertIn("not a credit approval", contract["method_limit"])
        self.assertIn("authority to fund", contract["method_limit"])


if __name__ == "__main__":
    unittest.main()

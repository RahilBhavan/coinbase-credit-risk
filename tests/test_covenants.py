import unittest

from scripts.build_covenant_plan import build


class CovenantPlanTests(unittest.TestCase):
    def test_every_monitoring_rule_has_one_covenant(self):
        payload = build()
        rows = payload["covenants"]
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({row["monitor_id"] for row in rows}), 8)
        self.assertEqual(payload["summary"], {
            "covenant_count": 8,
            "projected_pass_count": 2,
            "pre_funding_blocked_count": 1,
            "not_measured_count": 5,
        })

    def test_terms_preserve_draft_and_action_boundaries(self):
        payload = build()
        self.assertEqual(payload["enforceability_status"], "draft_only")
        self.assertIn("not executed", payload["method_limit"])
        for row in payload["covenants"]:
            self.assertTrue(row["cure_period"])
            self.assertTrue(row["breach_consequence"])
            self.assertEqual(row["enforceability_status"], "draft_only")


if __name__ == "__main__":
    unittest.main()

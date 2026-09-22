import unittest

from scripts.build_monitoring_plan import build


class MonitoringPlanTests(unittest.TestCase):
    def test_plan_separates_projection_from_unmeasured_private_evidence(self):
        payload = build()
        rows = {row["monitor_id"]: row for row in payload["rules"]}
        self.assertEqual(payload["activation_state"], "pre_funding_blocked")
        self.assertEqual(payload["summary"], {
            "rule_count": 8,
            "pass_projection_count": 2,
            "pre_funding_blocked_count": 1,
            "not_measured_count": 5,
        })
        self.assertEqual(rows["MON-01"]["current_value"], "1.269x")
        self.assertEqual(rows["MON-02"]["status"], "pre_funding_blocked")
        self.assertEqual(rows["MON-07"]["current_value"], "$1,000,000.00")

    def test_every_rule_has_an_owner_action_and_escalation(self):
        for row in build()["rules"]:
            self.assertTrue(row["owner_role"])
            self.assertTrue(row["breach_action"])
            self.assertTrue(row["escalation"])


if __name__ == "__main__":
    unittest.main()

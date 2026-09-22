import unittest

from scripts.build_escalation_playbook import build


class EscalationPlaybookTests(unittest.TestCase):
    def test_playbooks_map_one_to_one_across_controls(self):
        payload = build()
        rows = payload["playbooks"]
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({row["monitor_id"] for row in rows}), 8)
        self.assertEqual(len({row["covenant_id"] for row in rows}), 8)
        self.assertEqual(payload["summary"], {
            "playbook_count": 8,
            "critical_count": 3,
            "high_count": 4,
            "moderate_count": 1,
            "blocked_current_count": 1,
            "private_evidence_required_count": 5,
        })

    def test_current_state_never_implies_an_observed_incident(self):
        payload = build()
        self.assertEqual(payload["activation_state"], "pre_funding_blocked")
        self.assertIn("No incident is open", payload["method_limit"])
        allowed = {
            "projection_only_no_incident",
            "resolve_pre_funding_blocker",
            "obtain_private_evidence_before_activation",
        }
        for row in payload["playbooks"]:
            self.assertIn(row["current_response"], allowed)
            self.assertTrue(row["required_evidence"])
            self.assertTrue(row["exit_criteria"])
            self.assertTrue(row["decision_owner"])


if __name__ == "__main__":
    unittest.main()

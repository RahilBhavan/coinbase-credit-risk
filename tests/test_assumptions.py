import unittest

from scripts.build_assumption_register import build


class AssumptionRegisterTests(unittest.TestCase):
    def test_all_case_assumptions_are_governed(self):
        payload = build()
        self.assertEqual(payload["summary"], {
            "assumption_count": 7,
            "critical_count": 3,
            "high_count": 4,
            "unvalidated_count": 7,
            "downstream_lineage_link_count": 27,
        })
        self.assertEqual({row["assumption_id"] for row in payload["assumptions"]}, {f"ASM-C00{index}" for index in range(1, 8)})

    def test_assumptions_remain_explicitly_unvalidated(self):
        for row in build()["assumptions"]:
            self.assertEqual(row["validation_status"], "unvalidated")
            self.assertIn(row["evidence_class"], {"assumed", "simulated"})
            self.assertTrue(row["validation_method"])
            self.assertTrue(row["challenge_trigger"])

    def test_each_assumption_has_owner_and_downstream_impact(self):
        for row in build()["assumptions"]:
            self.assertTrue(row["owner_role"])
            self.assertTrue(row["workbook_inputs"])
            self.assertTrue(row["downstream_lineage_nodes"])


if __name__ == "__main__":
    unittest.main()

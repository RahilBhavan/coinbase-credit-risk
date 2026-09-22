import unittest

from scripts.build_diligence_plan import build


class DiligencePlanTests(unittest.TestCase):
    def test_plan_covers_conditions_and_is_executable(self):
        payload = build()
        rows = payload["tasks"]
        self.assertEqual(payload["summary"], {
            "task_count": 9,
            "critical_count": 4,
            "high_count": 5,
            "parallel_lane_count": 4,
            "wave_one_count": 8,
            "dependency_blocked_count": 1,
            "ready_to_start_count": 8,
        })
        self.assertEqual(len({row["condition_id"] for row in rows}), 9)
        self.assertEqual({row["wave"] for row in rows}, {1, 2})

    def test_control_agreement_waits_for_ownership_and_lien(self):
        rows = {row["condition_id"]: row for row in build()["tasks"]}
        self.assertEqual(rows["CP-03"]["depends_on"], ["CP-01", "CP-02"])
        self.assertEqual(rows["CP-03"]["wave"], 2)
        self.assertEqual(rows["CP-03"]["current_action"], "waiting_on:CP-01|CP-02")

    def test_each_task_names_impact_and_completion_evidence(self):
        for row in build()["tasks"]:
            self.assertTrue(row["affected_lineage_nodes"])
            self.assertTrue(row["failure_consequence"])
            self.assertTrue(row["completion_output"])
            self.assertIn(row["priority"], {"critical", "high"})


if __name__ == "__main__":
    unittest.main()

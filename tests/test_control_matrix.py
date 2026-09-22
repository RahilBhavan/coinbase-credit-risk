from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_control_matrix  # noqa: E402


class ControlMatrixTests(unittest.TestCase):
    def test_every_control_chain_is_complete_and_unique(self):
        payload = build_control_matrix.build()
        rows = payload["controls"]
        self.assertEqual(len(rows), 8)
        for field in ("control_id", "monitor_id", "covenant_id", "playbook_id"):
            values = [row[field] for row in rows]
            self.assertEqual(len(values), len(set(values)))

    def test_every_condition_is_covered(self):
        payload = build_control_matrix.build()
        covered = {condition for row in payload["controls"] for condition in row["condition_ids"]}
        self.assertEqual(covered, {"CP-01", "CP-02", "CP-03", "CP-04", "DD-01", "DD-02", "DD-03", "DD-04", "PF-01"})

    def test_current_state_preserves_pre_funding_boundary(self):
        payload = build_control_matrix.build()
        self.assertEqual(payload["activation_state"], "pre_funding_blocked")
        self.assertEqual(payload["enforceability_status"], "draft_only")
        self.assertTrue(all(row["condition_status"] == "outstanding" for row in payload["controls"]))
        self.assertIn("do not evidence completed conditions", payload["method_limit"])


if __name__ == "__main__":
    unittest.main()

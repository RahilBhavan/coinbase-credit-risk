from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_reviewer_scorecard  # noqa: E402


class ReviewerScorecardTests(unittest.TestCase):
    def test_scorecard_preserves_all_outstanding_gates(self):
        payload = build_reviewer_scorecard.build()
        self.assertEqual([row["gate_id"] for row in payload["gates"]], ["HG-01", "HG-02", "HG-03"])
        self.assertEqual(payload["summary"], {"gate_count": 3, "passed_count": 0, "outstanding_count": 3})
        self.assertTrue(all(row["current_status"] == "OUTSTANDING" for row in payload["gates"]))

    def test_each_gate_is_executable(self):
        for gate in build_reviewer_scorecard.build()["gates"]:
            self.assertTrue(gate["reviewer_role"])
            self.assertGreaterEqual(len(gate["review_questions"]), 4)
            self.assertGreaterEqual(len(gate["pass_criteria"]), 3)
            self.assertTrue(gate["required_evidence"])

    def test_scorecard_uses_valid_governed_pass_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            evidence_root = Path(temporary)
            evidence = evidence_root / "evidence" / "hg-01.txt"
            evidence.parent.mkdir()
            evidence.write_text("Independent calculation and conclusion\n", encoding="utf-8")
            outstanding = lambda gate_id: {
                "gate_id": gate_id, "outcome": "OUTSTANDING", "reviewer_identifier": "",
                "reviewer_role": "", "reviewed_on": "", "attribution_permission": "",
                "criterion_results": [], "evidence_paths": [], "notes": "", "recorded_at": "",
            }
            ledger = {
                "records": [
                    {
                        "gate_id": "HG-01", "outcome": "PASS", "reviewer_identifier": "reviewer-1",
                        "reviewer_role": "Independent model reviewer", "reviewed_on": "2026-09-20",
                        "attribution_permission": "ROLE_ONLY", "criterion_results": ["PASS", "PASS", "PASS"],
                        "evidence_paths": ["evidence/hg-01.txt"], "notes": "Reproduced independently.",
                        "recorded_at": "2026-09-20T12:00:00Z",
                    },
                    outstanding("HG-02"),
                    outstanding("HG-03"),
                ]
            }
            payload = build_reviewer_scorecard.build(ledger, evidence_root)
            self.assertEqual(payload["summary"], {"gate_count": 3, "passed_count": 1, "outstanding_count": 2})
            self.assertEqual([row["current_status"] for row in payload["gates"]], ["PASS", "OUTSTANDING", "OUTSTANDING"])


if __name__ == "__main__":
    unittest.main()

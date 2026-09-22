from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import reviewer_evidence  # noqa: E402


class ReviewerEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.payload = reviewer_evidence.load()

    def test_delivered_ledger_has_no_passed_gates(self):
        self.assertEqual(reviewer_evidence.validate_ledger(self.payload), [])
        self.assertFalse(any(reviewer_evidence.gate_passes(row) for row in self.payload["records"]))

    def test_pass_without_complete_evidence_is_rejected(self):
        record = copy.deepcopy(self.payload["records"][0])
        record["outcome"] = "PASS"
        errors = reviewer_evidence.validate_record(record)
        self.assertIn("reviewer_identifier is required for a completed review", errors)
        self.assertIn("at least one evidence path is required", errors)

    def test_complete_pass_with_retained_evidence_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "evidence" / "hg-01.md"
            evidence.parent.mkdir()
            evidence.write_text("Independent calculation steps and conclusion.\n")
            record = {
                "gate_id": "HG-01", "outcome": "PASS", "reviewer_identifier": "Reviewer A",
                "reviewer_role": "Independent model reviewer", "reviewed_on": "2026-09-20",
                "attribution_permission": "ROLE_ONLY", "criterion_results": ["PASS", "PASS", "PASS"],
                "evidence_paths": ["evidence/hg-01.md"], "notes": "Reproduced independently.",
                "recorded_at": "2026-09-20T18:00:00+00:00",
            }
            self.assertEqual(reviewer_evidence.validate_record(record, root), [])
            self.assertTrue(reviewer_evidence.gate_passes(record, root))

    def test_atomic_write_round_trips(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            reviewer_evidence.write_atomic(self.payload, path)
            self.assertEqual(json.loads(path.read_text()), self.payload)


if __name__ == "__main__":
    unittest.main()

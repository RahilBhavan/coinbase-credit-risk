import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_review_bundle", ROOT / "scripts/build_review_bundle.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ReviewBundleTests(unittest.TestCase):
    def test_start_guide_and_manifest_boundary_follow_gate_state(self):
        readiness = {"local_acceptance_verified": True, "ready_to_share": False, "human_gates": [
            {"id": "HG-01", "status": "PASS"},
            {"id": "HG-02", "status": "OUTSTANDING"},
            {"id": "HG-03", "status": "PASS"},
        ]}
        guide = MODULE.build_start_here(readiness)
        self.assertIn("2 of 3 human gates passed and 1 outstanding", guide)
        self.assertEqual(
            MODULE.evidence_boundary(readiness),
            "locally verified; 2 of 3 human gates passed; legal validation outstanding",
        )

    def test_start_guide_rejects_unknown_gate_status(self):
        readiness = {"human_gates": [{"id": "HG-01", "status": "PENDING"}]}
        with self.assertRaisesRegex(ValueError, "unsupported human-gate status"):
            MODULE.build_start_here(readiness)


if __name__ == "__main__":
    unittest.main()

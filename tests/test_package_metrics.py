import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_package_metrics", ROOT / "scripts/build_package_metrics.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PackageMetricsTests(unittest.TestCase):
    def test_passed_gate_count_uses_governed_status_vocabulary(self):
        readiness = {"human_gates": [
            {"id": "HG-01", "status": "PASS"},
            {"id": "HG-02", "status": "OUTSTANDING"},
            {"id": "HG-03", "status": "PASS"},
        ]}
        self.assertEqual(MODULE.passed_human_gate_count(readiness), 2)

    def test_package_metrics_match_authoritative_artifacts(self):
        MODULE.main()
        metrics = json.loads((ROOT / "artifacts/package-metrics.json").read_text())
        self.assertEqual(metrics["workbook"]["sheet_count"], 16)
        self.assertEqual(metrics["workbook"]["audit_pass_count"], metrics["workbook"]["audit_check_count"])
        self.assertEqual(metrics["decision_support"]["scenario_count"], 11)
        self.assertEqual(metrics["decision_support"]["condition_count"], 9)
        self.assertEqual(metrics["review"]["human_gates_passed"], 0)
        self.assertFalse(metrics["review"]["ready_to_share"])

    def test_package_metrics_markdown_exposes_review_boundary(self):
        MODULE.main()
        text = (ROOT / "artifacts/package-metrics.md").read_text()
        self.assertIn("| Human gates passed | 0 / 3 |", text)
        self.assertIn("| Ready to share | false |", text)

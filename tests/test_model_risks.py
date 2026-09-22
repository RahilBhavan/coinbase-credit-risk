import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ModelRiskRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads((ROOT / "artifacts/model-risk-register.json").read_text())

    def test_every_open_risk_has_governance_and_disposition(self):
        for risk in self.payload["risks"]:
            self.assertEqual(risk["status"], "open")
            self.assertTrue(risk["owner"])
            self.assertTrue(risk["mitigation"])
            self.assertTrue(risk["validation_evidence"])
            self.assertTrue(risk["disposition_if_unresolved"])

    def test_critical_risks_map_to_assumptions_and_conditions(self):
        critical = [risk for risk in self.payload["risks"] if risk["severity"] == "critical"]
        self.assertEqual(len(critical), 3)
        for risk in critical:
            self.assertTrue(risk["linked_assumptions"])
            self.assertTrue(risk["linked_conditions"])

    def test_implementation_risk_preserves_human_gate_boundary(self):
        risk = next(row for row in self.payload["risks"] if row["risk_id"] == "MR-08")
        self.assertIn("not ready to share", risk["disposition_if_unresolved"])

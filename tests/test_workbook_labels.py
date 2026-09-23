import unittest
from pathlib import Path

from credit_risk.engine import evaluate_case
from scripts.audit_workbook import WORKBOOK, load_workbook


CASE_DIR = Path(__file__).resolve().parents[1] / "data" / "case"


class WorkbookLabelTests(unittest.TestCase):
    def test_summary_recommendation_label_follows_recommended_amount(self):
        summary = load_workbook(WORKBOOK)["Summary"]
        self.assertIn("TEXT(D14", summary["D15"].formula)
        amount = int(evaluate_case(CASE_DIR, "base")["recommended_amount_usd"].split(".")[0])
        self.assertEqual(summary["D15"].value, f"APPROVE ${amount / 1_000_000:.1f}M SUBJECT TO SIMULATED CONDITIONS PRECEDENT")


if __name__ == "__main__":
    unittest.main()

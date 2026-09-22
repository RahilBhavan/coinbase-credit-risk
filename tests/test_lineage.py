import re
import unittest
from pathlib import Path

from scripts.build_decision_lineage import ROOT, build


class DecisionLineageTests(unittest.TestCase):
    def test_lineage_covers_committee_headlines(self):
        payload = build()
        claims = {row["committee_claim"] for row in payload["nodes"]}
        self.assertEqual(payload["summary"], {
            "node_count": 11,
            "source_link_count": 32,
            "reported_supported_node_count": 4,
            "assumption_exposed_node_count": 10,
        })
        self.assertTrue({"Requested commitment", "Illustrative obligor rating", "Recommended conditional limit", "Funding gate"}.issubset(claims))

    def test_every_reference_resolves(self):
        for row in build()["nodes"]:
            artifact = ROOT / row["artifact_locator"].split("#", 1)[0]
            self.assertTrue(artifact.is_file(), row["node_id"])
            self.assertRegex(row["workbook_locator"], r"^[A-Za-z ]+![A-Z]+[0-9]+$")
            self.assertTrue(row["evidence_ids"])
            self.assertTrue(row["owner_role"])
            self.assertTrue(row["limitation"])

    def test_current_values_match_decision_contract(self):
        rows = {row["node_id"]: row for row in build()["nodes"]}
        self.assertEqual(rows["LIN-04"]["current_value"], "3870600.00")
        self.assertEqual(rows["LIN-08"]["current_value"], "3000000.00")
        self.assertEqual(rows["LIN-09"]["current_value"], "blocked_pending_conditions")
        self.assertEqual(rows["LIN-10"]["current_value"], "-194790000.00")
        self.assertEqual(rows["LIN-11"]["current_value"], "1")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import extract_filing_facts  # noqa: E402


class FilingEvidenceTests(unittest.TestCase):
    def test_xbrl_extractor_prefers_highest_precision_duplicate(self):
        document = """
        <ix:nonFraction name="us-gaap:Example" contextRef="c-1" decimals="-6" scale="6">421.3</ix:nonFraction>
        <ix:nonFraction name="us-gaap:Example" contextRef="c-1" decimals="-3" scale="3">421,274</ix:nonFraction>
        """
        self.assertEqual(
            extract_filing_facts.xbrl_value(document, "us-gaap:Example", "c-1"),
            Decimal("421274000"),
        )

    def test_all_declared_filing_reconciliations_pass(self):
        facts = extract_filing_facts.build_facts()
        self.assertEqual(len(facts), 13)
        self.assertEqual(len({fact.fact_id for fact in facts}), len(facts))
        for fact in facts:
            with self.subTest(fact_id=fact.fact_id):
                self.assertLessEqual(abs(fact.filing_value - fact.model_value), fact.tolerance)


if __name__ == "__main__":
    unittest.main()

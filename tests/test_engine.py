import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from credit_risk.engine import evaluate_all, evaluate_case


CASE_DIR = Path(__file__).resolve().parents[1] / "data" / "case"


class EngineTests(unittest.TestCase):
    def _modified_case(self, filename, mutate):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        for source in CASE_DIR.glob("*.json"):
            (root / source.name).write_bytes(source.read_bytes())
        path = root / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        mutate(payload)
        path.write_text(json.dumps(payload), encoding="utf-8")
        self.addCleanup(temporary.cleanup)
        return root

    def test_lower_price_cannot_increase_available_proceeds(self):
        base = evaluate_case(CASE_DIR, "base")
        stressed = evaluate_case(CASE_DIR, "collateral_down_30")
        self.assertLessEqual(
            Decimal(stressed["available_proceeds_usd"]),
            Decimal(base["available_proceeds_usd"]),
        )

    def test_higher_funded_exposure_cannot_reduce_shortfall(self):
        base = evaluate_case(CASE_DIR)
        root = self._modified_case(
            "facility.json",
            lambda facility: facility.update({"funded_exposure_usd": "7000000"}),
        )
        increased = evaluate_case(root)
        self.assertGreaterEqual(
            Decimal(increased["shortfall_usd"]), Decimal(base["shortfall_usd"])
        )

    def test_unknown_enforceability_blocks_and_grants_no_credit(self):
        root = self._modified_case(
            "collateral.json",
            lambda rows: rows[0].update({"legal_control": "unknown"}),
        )
        result = evaluate_case(root)
        self.assertEqual(result["available_proceeds_usd"], "0.00")
        self.assertEqual(result["recommended_amount_usd"], "0.00")
        self.assertIn("SIM-USDC-BASE-01:legal_control_not_enforceable", result["hard_blockers"])

    def test_declared_scenario_suite_is_complete_and_directional(self):
        results = {row["scenario_id"]: row for row in evaluate_all(CASE_DIR)}
        self.assertEqual(len(results), 11)
        self.assertEqual(results["stale_price"]["decision"], "decline")
        self.assertIn("SIM-USDC-BASE-01:price_stale", results["stale_price"]["hard_blockers"])
        self.assertEqual(results["zero_collateral"]["available_proceeds_usd"], "0.00")
        self.assertEqual(results["missing_ownership_evidence"]["decision"], "decline")
        self.assertEqual(results["borrower_cash_stress"]["recommended_amount_usd"], "2000000.00")
        self.assertEqual(results["borrower_cash_stress"]["binding_cap"], "obligor")
        self.assertEqual(results["correlated_portfolio_stress"]["recommended_amount_usd"], "1000000.00")
        self.assertEqual(results["correlated_portfolio_stress"]["binding_cap"], "concentration")
        self.assertLess(
            Decimal(results["canonical_withdrawal_168h"]["available_proceeds_usd"]),
            Decimal(results["route_delay_24h"]["available_proceeds_usd"]),
        )

    def test_decision_record_contract_is_complete_and_traced(self):
        result = evaluate_case(CASE_DIR, "base")
        required = {
            "illustrative_rating", "rating_rationale", "reversal_trigger",
            "source_coverage_rate", "source_coverage_scope", "preparer",
            "review_status", "calculation_trace", "condition_register",
            "outstanding_blocking_conditions", "funding_gate_status",
            "rating_score", "rating_factors", "rating_scale", "rating_method_limit",
            "exposure_basis", "recommended_pro_forma_exposure_usd",
            "recommended_pro_forma_coverage_surplus_usd",
        }
        self.assertTrue(required.issubset(result))
        self.assertEqual(result["source_coverage_rate"], "1.0")
        self.assertEqual(
            result["calculation_trace"]["rounded_recommended_amount_usd"],
            result["recommended_amount_usd"],
        )
        self.assertIn("independent practitioner review outstanding", result["review_status"])
        self.assertEqual(result["rating_score"], "3.10")
        self.assertEqual(result["illustrative_rating"], "3 / Watchful")
        self.assertEqual(len(result["rating_factors"]), 5)
        self.assertEqual(result["exposure_usd"], "5050000.00")
        self.assertEqual(result["shortfall_usd"], "1179400.00")
        self.assertEqual(result["recommended_pro_forma_exposure_usd"], "3050000.00")
        self.assertEqual(result["recommended_pro_forma_coverage_surplus_usd"], "820600.00")
        self.assertIn("requested fully drawn recovery case", result["exposure_basis"])

    def test_declined_case_has_no_recommended_pro_forma_exposure(self):
        result = evaluate_case(CASE_DIR, "route_failure")
        self.assertEqual(result["decision"], "decline")
        self.assertEqual(result["recommended_pro_forma_exposure_usd"], "0.00")
        self.assertEqual(result["recommended_pro_forma_coverage_surplus_usd"], "0.00")

    def test_worsening_a_rating_factor_cannot_improve_score(self):
        base = evaluate_case(CASE_DIR, "base")
        root = self._modified_case(
            "rating.json",
            lambda rating: rating["factors"][0].update({"score": "2"}),
        )
        worsened = evaluate_case(root, "base")
        self.assertGreaterEqual(Decimal(worsened["rating_score"]), Decimal(base["rating_score"]))

    def test_conditional_approval_is_not_cleared_to_fund(self):
        result = evaluate_case(CASE_DIR, "base")
        self.assertEqual(result["decision"], "approve_reduced")
        self.assertEqual(result["funding_gate_status"], "blocked_pending_conditions")
        self.assertEqual(len(result["condition_register"]), 9)
        self.assertEqual(len(result["outstanding_blocking_conditions"]), 9)
        root = self._modified_case(
            "conditions.json",
            lambda rows: [row.update({"evidence_status": "verified"}) for row in rows],
        )
        cleared = evaluate_case(root, "base")
        self.assertEqual(cleared["funding_gate_status"], "cleared_to_fund")
        self.assertEqual(cleared["outstanding_blocking_conditions"], [])

    def test_route_delay_reduces_only_matching_route_proceeds(self):
        base = evaluate_case(CASE_DIR, "base")
        delayed = evaluate_case(CASE_DIR, "route_delay_24h")
        self.assertLess(
            Decimal(delayed["available_proceeds_usd"]),
            Decimal(base["available_proceeds_usd"]),
        )
        self.assertEqual(delayed["collateral_lots"][0]["effective_delay_hours"], "26")

    def test_tighter_concentration_limit_cannot_raise_recommendation(self):
        base = evaluate_case(CASE_DIR)
        root = self._modified_case(
            "policy.json",
            lambda policy: policy.update({"collateral_asset_concentration_limit": "0.25"}),
        )
        tighter = evaluate_case(root)
        self.assertLessEqual(
            Decimal(tighter["recommended_amount_usd"]),
            Decimal(base["recommended_amount_usd"]),
        )
        self.assertEqual(tighter["caps_usd"]["concentration"], "0.00")

    def test_route_failure_is_a_hard_blocker(self):
        result = evaluate_case(CASE_DIR, "route_failure")
        self.assertEqual(result["decision"], "decline")
        self.assertIn("SIM-USDC-BASE-01:repayment_route_unavailable", result["hard_blockers"])


if __name__ == "__main__":
    unittest.main()

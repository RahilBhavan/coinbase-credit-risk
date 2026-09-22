#!/usr/bin/env python3
"""Explain each scenario's decision change without adding new credit logic."""

from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_OUTPUT = ROOT / "artifacts" / "scenario-attribution.json"
CSV_OUTPUT = ROOT / "artifacts" / "scenario-attribution.csv"


DRIVER_DETAILS = {
    "base": ("reference_case", "Complete and verify every blocking pre-funding condition."),
    "collateral_down_30": ("collateral_market_value", "Add eligible collateral, repay exposure, or reduce the commitment."),
    "collateral_down_50": ("collateral_market_value", "Add eligible collateral, repay exposure, or reduce the commitment."),
    "stale_price": ("price_integrity_blocker", "Obtain a fresh independent price within the approved staleness tolerance."),
    "zero_collateral": ("collateral_availability", "Verify accessible quantity in controlled custody or provide eligible replacement collateral."),
    "route_delay_24h": ("route_timing_cost", "Complete a timed route test and evidence proceeds, fees, and destination."),
    "canonical_withdrawal_168h": ("route_timing_cost", "Use a faster approved route, add collateral, or reduce the commitment."),
    "route_failure": ("repayment_route_blocker", "Complete a successful end-to-end collateral-to-bank repayment test."),
    "missing_ownership_evidence": ("ownership_blocker", "Provide independently corroborated beneficial-ownership and custody records."),
    "borrower_cash_stress": ("obligor_capacity", "Reconcile a 13-week borrowing-entity cash forecast and complete debt-service schedule."),
    "correlated_portfolio_stress": ("portfolio_concentration", "Obtain current portfolio capacity, limit-owner approval, and refreshed borrower downside evidence."),
}


def build() -> dict:
    scenarios = json.loads((ROOT / "artifacts" / "scenario-results.json").read_text(encoding="utf-8"))
    base = next(row for row in scenarios if row["scenario_id"] == "base")
    base_recommendation = Decimal(base["recommended_amount_usd"])
    base_proceeds = Decimal(base["available_proceeds_usd"])
    rows = []
    for scenario in scenarios:
        recommendation = Decimal(scenario["recommended_amount_usd"])
        proceeds = Decimal(scenario["available_proceeds_usd"])
        if recommendation == base_recommendation:
            change_class = "same_limit"
        elif recommendation == 0:
            change_class = "decline"
        else:
            change_class = "reduced_limit"
        primary_driver, resolution_evidence = DRIVER_DETAILS[scenario["scenario_id"]]
        rows.append({
            "scenario_id": scenario["scenario_id"],
            "decision": scenario["decision"],
            "change_class": change_class,
            "recommended_amount_usd": scenario["recommended_amount_usd"],
            "recommendation_delta_vs_base_usd": str((recommendation - base_recommendation).quantize(Decimal("0.01"))),
            "available_proceeds_usd": scenario["available_proceeds_usd"],
            "proceeds_delta_vs_base_usd": str((proceeds - base_proceeds).quantize(Decimal("0.01"))),
            "binding_cap": scenario["binding_cap"],
            "primary_driver": primary_driver,
            "hard_blockers": scenario["hard_blockers"],
            "resolution_evidence": resolution_evidence,
        })
    ranked = sorted(rows, key=lambda row: (Decimal(row["recommended_amount_usd"]), Decimal(row["available_proceeds_usd"]), row["scenario_id"]))
    rank_by_id = {row["scenario_id"]: index for index, row in enumerate(ranked, start=1)}
    for row in rows:
        row["severity_rank"] = rank_by_id[row["scenario_id"]]
    return {
        "schema_version": "1.0",
        "case_id": base["case_id"],
        "case_version": base["case_version"],
        "method_limit": "Attribution is a deterministic explanation of declared scenario outputs. It is not a probability, forecast, causal estimate, or new decision rule.",
        "summary": {
            "scenario_count": len(rows),
            "same_limit_count": sum(row["change_class"] == "same_limit" for row in rows),
            "reduced_limit_count": sum(row["change_class"] == "reduced_limit" for row in rows),
            "decline_count": sum(row["change_class"] == "decline" for row in rows),
            "hard_blocker_scenario_count": sum(bool(row["hard_blockers"]) for row in rows),
            "maximum_recommendation_loss_usd": str(max(Decimal("0"), max(-Decimal(row["recommendation_delta_vs_base_usd"]) for row in rows)).quantize(Decimal("0.01"))),
        },
        "rows": rows,
    }


def main() -> int:
    payload = build()
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["scenario_id", "severity_rank", "decision", "change_class", "recommended_amount_usd", "recommendation_delta_vs_base_usd", "available_proceeds_usd", "proceeds_delta_vs_base_usd", "binding_cap", "primary_driver", "hard_blockers", "resolution_evidence"]
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["rows"]:
            writer.writerow({**row, "hard_blockers": "|".join(row["hard_blockers"])})
    print(f"Scenario attribution: {payload['summary']['scenario_count']} scenarios; declines={payload['summary']['decline_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

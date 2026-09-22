#!/usr/bin/env python3
"""Build an illustrative collateral-call and commitment step-down ladder."""

from __future__ import annotations

import csv
import json
from decimal import Decimal, ROUND_DOWN
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data" / "case"
JSON_OUT = ROOT / "artifacts" / "collateral-call-ladder.json"
CSV_OUT = ROOT / "artifacts" / "collateral-call-ladder.csv"
CENT = Decimal("0.01")


def money(value: Decimal) -> str:
    return str(value.quantize(CENT))


def build() -> dict[str, object]:
    facility = json.loads((CASE / "facility.json").read_text())
    policy = json.loads((CASE / "policy.json").read_text())
    collateral = json.loads((CASE / "collateral.json").read_text())[0]
    config = json.loads((CASE / "collateral_calls.json").read_text())
    decision = json.loads((ROOT / "artifacts" / "decision-record.json").read_text())

    quantity = Decimal(collateral["quantity"])
    price = Decimal(collateral["quoted_price_usd"])
    execution = Decimal(collateral["execution_cost_bps"]) / Decimal("10000")
    delay = Decimal(collateral["earliest_usable_hours"]) * Decimal(policy["delay_cost_bps_per_hour"]) / Decimal("10000")
    variable_cost = execution + delay
    fixed_cost = Decimal(collateral["fixed_cost_usd"])
    coverage = Decimal(facility["required_coverage_ratio"])
    accrued = Decimal(facility["accrued_amount_usd"])
    commitment = Decimal(decision["recommended_amount_usd"])
    exposure = commitment + accrued
    required_proceeds = exposure * coverage
    increment = Decimal(policy["recommendation_increment_usd"])
    exact_trigger = Decimal("1") - ((required_proceeds + fixed_cost) / (quantity * price * (Decimal("1") - variable_cost)))

    rows = []
    for stress_text in config["stress_levels_pct"]:
        stress = Decimal(stress_text)
        unit_net = price * (Decimal("1") - stress) * (Decimal("1") - variable_cost)
        proceeds = max(Decimal("0"), quantity * unit_net - fixed_cost)
        ratio = proceeds / exposure
        headroom = proceeds - required_proceeds
        required_quantity = (required_proceeds + fixed_cost) / unit_net
        top_up = max(Decimal("0"), required_quantity - quantity)
        repayment = max(Decimal("0"), exposure - proceeds / coverage)
        max_commitment = max(Decimal("0"), proceeds / coverage - accrued)
        rounded_commitment = (max_commitment / increment).to_integral_value(rounding=ROUND_DOWN) * increment
        rows.append({
            "price_stress_pct": str(stress),
            "available_proceeds_usd": money(proceeds),
            "coverage_ratio": str(ratio.quantize(Decimal("0.0001"))),
            "status": "PASS" if headroom >= 0 else "CALL_REQUIRED",
            "required_proceeds_usd": money(required_proceeds),
            "covenant_headroom_usd": money(headroom),
            "top_up_required_usdc": money(top_up),
            "repayment_required_usd": money(repayment),
            "max_coverage_compliant_commitment_usd": money(max_commitment),
            "rounded_coverage_compliant_commitment_usd": money(rounded_commitment),
        })

    return {
        "schema_version": "1.0",
        "case_id": facility["case_id"],
        "evidence_class": config["evidence_class"],
        "recommended_commitment_usd": money(commitment),
        "accrued_amount_usd": money(accrued),
        "pro_forma_exposure_usd": money(exposure),
        "required_coverage_ratio": str(coverage),
        "required_proceeds_usd": money(required_proceeds),
        "exact_modeled_breach_price_stress_pct": str(exact_trigger.quantize(Decimal("0.000001"))),
        "first_grid_call_stress_pct": next(row["price_stress_pct"] for row in rows if row["status"] == "CALL_REQUIRED"),
        "rows": rows,
        "method_limit": config["method_limit"],
    }


def main() -> int:
    result = build()
    JSON_OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["rows"][0]))
        writer.writeheader()
        writer.writerows(result["rows"])
    print(f"Collateral-call ladder: {len(result['rows'])} rows; first grid call {result['first_grid_call_stress_pct']} -> {JSON_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

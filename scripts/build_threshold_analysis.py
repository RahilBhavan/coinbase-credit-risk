#!/usr/bin/env python3
"""Build transparent break-even thresholds for the MARA-CR-001 decision."""

from __future__ import annotations

import csv
import json
import sys
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_risk.engine import evaluate_case  # noqa: E402


ZERO = Decimal("0")
ONE = Decimal("1")


def load_json(name: str):
    return json.loads((ROOT / "data" / "case" / name).read_text(encoding="utf-8"))


def analyze() -> dict:
    facility = load_json("facility.json")
    lot = load_json("collateral.json")[0]
    policy = load_json("policy.json")
    base_scenario = next(row for row in load_json("scenarios.json") if row["scenario_id"] == "base")
    base = evaluate_case(ROOT / "data" / "case", "base")

    quantity = Decimal(lot["quantity"])
    price = Decimal(lot["quoted_price_usd"])
    fixed_cost = Decimal(lot["fixed_cost_usd"])
    coverage = Decimal(facility["required_coverage_ratio"])
    base_shock = Decimal(base_scenario["price_shock_pct"])
    effective_hours = Decimal(lot["earliest_usable_hours"]) + Decimal(base_scenario["additional_route_delay_hours"])
    execution_rate = (Decimal(lot["execution_cost_bps"]) + Decimal(base_scenario["extra_execution_cost_bps"])) / Decimal("10000")
    delay_rate = effective_hours * Decimal(policy["delay_cost_bps_per_hour"]) / Decimal("10000")
    post_cost_factor = ONE - execution_rate - delay_rate
    base_unit_proceeds = price * (ONE - base_shock) * post_cost_factor

    targets = [Decimal("2000000"), Decimal("3000000"), Decimal("4000000"), Decimal("5000000")]
    max_price_declines = {}
    required_quantities = {}
    for target in targets:
        required_proceeds = target * coverage
        max_decline = ONE - (required_proceeds + fixed_cost) / (quantity * price * post_cost_factor)
        required_quantity = (required_proceeds + fixed_cost) / base_unit_proceeds
        key = str(int(target))
        max_price_declines[key] = str(max(ZERO, min(ONE, max_decline)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))
        required_quantities[key] = str(required_quantity.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    non_collateral_caps = {name: Decimal(value) for name, value in base["caps_usd"].items() if name != "collateral"}
    limiting_name = min(non_collateral_caps, key=lambda name: (non_collateral_caps[name], name))
    max_non_collateral_limit = non_collateral_caps[limiting_name]
    requested = Decimal(facility["requested_commitment_usd"])
    increment = Decimal(policy["recommendation_increment_usd"])
    quantity_grid = [Decimal(value) for value in ("2000000", "3000000", "4000000", "5000000", "6000000")]
    stress_grid = [Decimal(value) for value in ("0", "0.02", "0.05", "0.10", "0.20", "0.30", "0.40", "0.50")]
    decision_surface = []
    for grid_quantity in quantity_grid:
        for grid_stress in stress_grid:
            gross = grid_quantity * price * (ONE - grid_stress)
            proceeds = max(ZERO, gross * post_cost_factor - fixed_cost)
            collateral_cap = proceeds / coverage
            caps = {**non_collateral_caps, "collateral": collateral_cap, "requested": requested}
            raw_limit = min(caps.values())
            recommendation = (raw_limit / increment).quantize(ZERO, rounding=ROUND_DOWN) * increment
            binding = min(caps, key=lambda name: (caps[name], name))
            decision_surface.append({
                "collateral_quantity_usdc": str(grid_quantity.quantize(Decimal("0.01"))),
                "price_stress_pct": str(grid_stress),
                "available_proceeds_usd": str(proceeds.quantize(Decimal("0.01"))),
                "collateral_cap_usd": str(collateral_cap.quantize(Decimal("0.01"))),
                "recommended_amount_usd": str(recommendation.quantize(Decimal("0.01"))),
                "binding_cap": binding,
            })
    return {
        "case_id": facility["case_id"],
        "case_version": facility["case_version"],
        "base_recommendation_usd": base["recommended_amount_usd"],
        "base_available_proceeds_usd": base["available_proceeds_usd"],
        "post_cost_factor_before_price_stress": str(post_cost_factor),
        "max_price_decline_for_target": max_price_declines,
        "required_collateral_quantity_for_target": required_quantities,
        "maximum_non_collateral_limit_usd": str(max_non_collateral_limit.quantize(Decimal("0.01"))),
        "maximum_non_collateral_limit_name": limiting_name,
        "full_request_feasible_under_current_caps": max_non_collateral_limit >= requested,
        "decision_surface": {
            "quantity_axis_usdc": [str(value.quantize(Decimal("0.01"))) for value in quantity_grid],
            "price_stress_axis_pct": [str(value) for value in stress_grid],
            "cells": decision_surface,
        },
        "interpretation": "Thresholds hold execution, delay, fixed cost, coverage, and all non-target drivers constant. They are sensitivities, not forecasts.",
    }


def main() -> int:
    result = analyze()
    json_path = ROOT / "artifacts" / "threshold-analysis.json"
    csv_path = ROOT / "artifacts" / "threshold-analysis.csv"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = []
    for target, value in result["max_price_decline_for_target"].items():
        rows.append({"metric": "max_price_decline", "target_recommendation_usd": target, "value": value, "unit": "ratio", "collateral_quantity_usdc": "", "price_stress_pct": "", "binding_cap": ""})
    for target, value in result["required_collateral_quantity_for_target"].items():
        rows.append({"metric": "required_collateral_quantity", "target_recommendation_usd": target, "value": value, "unit": "USDC", "collateral_quantity_usdc": "", "price_stress_pct": "", "binding_cap": ""})
    rows.append({"metric": "maximum_non_collateral_limit", "target_recommendation_usd": "", "value": result["maximum_non_collateral_limit_usd"], "unit": "USD", "collateral_quantity_usdc": "", "price_stress_pct": "", "binding_cap": ""})
    for row in result["decision_surface"]["cells"]:
        rows.append({
            "metric": "decision_surface_recommendation", "target_recommendation_usd": "",
            "value": row["recommended_amount_usd"], "unit": "USD",
            "collateral_quantity_usdc": row["collateral_quantity_usdc"],
            "price_stress_pct": row["price_stress_pct"], "binding_cap": row["binding_cap"],
        })
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "target_recommendation_usd", "value", "unit", "collateral_quantity_usdc", "price_stress_pct", "binding_cap"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Threshold analysis: {len(rows)} metrics -> {json_path.relative_to(ROOT)}, {csv_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

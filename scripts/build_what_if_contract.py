#!/usr/bin/env python3
"""Build a browser-safe what-if contract from the authoritative case inputs."""

from __future__ import annotations

import json
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data" / "case"
OUTPUT = ROOT / "artifacts" / "what-if-contract.json"
ZERO = Decimal("0")


def money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def evaluate(contract: dict, inputs: dict) -> dict:
    blockers = sorted(name for name, verified in inputs["controls"].items() if not verified)
    quantity = Decimal(str(inputs["quantity_usdc"]))
    stress = Decimal(str(inputs["price_stress_pct"]))
    delay = Decimal(str(inputs["additional_route_delay_hours"])) + Decimal(contract["base_route_delay_hours"])
    execution_bps = Decimal(str(inputs["execution_cost_bps"]))
    gross = quantity * Decimal(contract["quoted_price_usd"]) * max(ZERO, Decimal("1") - stress)
    execution_cost = gross * execution_bps / Decimal("10000")
    delay_cost = gross * delay * Decimal(contract["delay_cost_bps_per_hour"]) / Decimal("10000")
    available = ZERO if blockers else max(ZERO, gross - execution_cost - delay_cost - Decimal(contract["fixed_cost_usd"]))
    collateral_cap = available / Decimal(contract["required_coverage_ratio"])
    caps = {
        "obligor": Decimal(contract["obligor_cap_usd"]),
        "collateral": collateral_cap,
        "single_name": Decimal(contract["single_name_cap_usd"]),
        "concentration": Decimal(contract["concentration_cap_usd"]),
    }
    binding = "hard_blocker" if blockers else min(caps, key=lambda name: (caps[name], name))
    raw = ZERO if blockers else min(Decimal(contract["requested_commitment_usd"]), *caps.values())
    increment = Decimal(contract["recommendation_increment_usd"])
    recommended = ZERO if raw == ZERO else (raw / increment).quantize(ZERO, rounding=ROUND_DOWN) * increment
    pro_forma = recommended + Decimal(contract["accrued_amount_usd"]) if recommended else ZERO
    return {
        "available_proceeds_usd": money(available),
        "collateral_cap_usd": money(collateral_cap),
        "recommended_amount_usd": money(recommended),
        "recommended_pro_forma_exposure_usd": money(pro_forma),
        "coverage_surplus_usd": money(max(ZERO, available - pro_forma)),
        "binding_cap": binding,
        "hard_blockers": blockers,
        "decision": "decline" if blockers or recommended == ZERO else "approve" if recommended >= Decimal(contract["requested_commitment_usd"]) else "approve_reduced",
    }


def build() -> dict:
    facility = json.loads((CASE / "facility.json").read_text(encoding="utf-8"))
    lot = json.loads((CASE / "collateral.json").read_text(encoding="utf-8"))[0]
    policy = json.loads((CASE / "policy.json").read_text(encoding="utf-8"))
    scenarios = json.loads((CASE / "scenarios.json").read_text(encoding="utf-8"))
    base = next(row for row in scenarios if row["scenario_id"] == "base")
    decision = json.loads((ROOT / "artifacts" / "decision-record.json").read_text(encoding="utf-8"))
    contract = {
        "schema_version": "1.0",
        "case_id": facility["case_id"],
        "case_version": facility["case_version"],
        "evidence_class": "simulated",
        "method_limit": "Interactive sensitivity only. Results are not a credit approval, a market forecast, observed collateral, or authority to fund.",
        "requested_commitment_usd": facility["requested_commitment_usd"],
        "accrued_amount_usd": facility["accrued_amount_usd"],
        "required_coverage_ratio": facility["required_coverage_ratio"],
        "obligor_cap_usd": policy["obligor_cap_usd"],
        "single_name_cap_usd": policy["single_name_cap_usd"],
        "concentration_cap_usd": decision["caps_usd"]["concentration"],
        "recommendation_increment_usd": policy["recommendation_increment_usd"],
        "quoted_price_usd": lot["quoted_price_usd"],
        "base_route_delay_hours": lot["earliest_usable_hours"],
        "delay_cost_bps_per_hour": policy["delay_cost_bps_per_hour"],
        "fixed_cost_usd": lot["fixed_cost_usd"],
        "defaults": {
            "quantity_usdc": lot["quantity"],
            "price_stress_pct": base.get("price_shock_pct", "0"),
            "additional_route_delay_hours": "0",
            "execution_cost_bps": lot["execution_cost_bps"],
            "controls": {"ownership": True, "first_priority": True, "legal_control": True, "route_available": True},
        },
        "bounds": {
            "quantity_usdc": {"minimum": "0", "maximum": "6000000", "step": "100000"},
            "price_stress_pct": {"minimum": "0", "maximum": "0.60", "step": "0.01"},
            "additional_route_delay_hours": {"minimum": "0", "maximum": "168", "step": "1"},
            "execution_cost_bps": {"minimum": "0", "maximum": "300", "step": "5"},
        },
    }
    vectors = []
    for vector_id, changes in (
        ("base", {}),
        ("price_down_50", {"price_stress_pct": "0.50"}),
        ("route_delay_24h", {"additional_route_delay_hours": "24"}),
        ("ownership_blocker", {"controls": {**contract["defaults"]["controls"], "ownership": False}}),
    ):
        inputs = {**contract["defaults"], **changes}
        vectors.append({"vector_id": vector_id, "inputs": inputs, "expected": evaluate(contract, inputs)})
    contract["test_vectors"] = vectors
    return contract


def main() -> int:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"What-if contract: {len(payload['test_vectors'])} reconciled vectors -> {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
